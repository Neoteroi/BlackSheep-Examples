# -*- coding: utf-8 -*-

import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from json import JSONEncoder
from typing import Any, Iterable, List, Literal, Optional, Union
from uuid import UUID, uuid4

import jwt
from blacksheep import Application
from blacksheep.messages import Request, Response
from blacksheep.server.authorization import allow_anonymous
from blacksheep.server.headers.cache import cache_control
from blacksheep.server.responses import json, no_content
from essentials.exceptions import UnauthorizedException
from guardpost.asynchronous.authentication import AuthenticationHandler
from guardpost.authentication import Identity
from guardpost.authorization import Policy
from guardpost.common import AuthenticatedRequirement
from jwt import InvalidTokenError
from pydantic import UUID4, BaseModel

from .user import UserDAL, checkpw

logger = logging.getLogger(__name__)


class UUIDJSONEncode(JSONEncoder):
    def default(self, obj: Any):
        if isinstance(obj, UUID):
            return obj.hex
        return JSONEncoder.default(self, obj)


class TokenPayload(BaseModel):
    """Token model."""

    sub: UUID4
    jti: UUID4
    sid: UUID4
    iat: datetime
    nbf: datetime
    exp: datetime
    typ: Literal["access", "refresh"]


class HMACAlgorithm(Enum):
    """HMAC algorithms."""

    HS256 = "HS256"
    HS384 = "HS384"
    HS512 = "HS512"


@dataclass
class OAuth2PasswordAuthData:
    """Dataclass for OAuth2 Password flow."""

    username: Optional[str] = None
    password: Optional[str] = None


@dataclass
class OAuth2PasswordRefreshData:
    """Dataclass for OAuth2 Password flow."""

    refresh_token: Optional[str] = None


@dataclass
class OAuth2PasswordSettings:
    """Settings for OAuth2 Password flow."""

    secret: str
    algorithm: HMACAlgorithm = HMACAlgorithm.HS256
    issuer: Optional[str] = None
    audience: Optional[Union[str, Iterable[str]]] = None
    token_path: str = "/token"
    refresh_path: str = "/refresh"
    revoke_path: str = "/revoke"
    access_token_ttl: int = 60 * 60
    refresh_token_ttl: int = 60 * 60 * 24 * 30
    username_field: str = "username"
    password_field: str = "password"


class FailedTokenDecode(Exception):
    """Raised when a token cannot be decoded."""


class HMACJWTSerializerBase:
    """Base class for JWT token generatoration/extraction."""

    def __init__(
        self,
        secret: str,
        algorithm: HMACAlgorithm = HMACAlgorithm.HS256,
        issuer: Optional[str] = None,
        audience: Optional[Union[str, Iterable[str]]] = None,
        verify_options: Optional[dict[str, Any]] = None,
    ):
        self.secret = secret
        self.algorithm = algorithm
        self.issuer = issuer
        self.audience = audience
        self.verify_options = verify_options

    def encode(self, payload: dict) -> str:
        """Encode a payload into a JWT token."""
        raise NotImplementedError()

    def decode(self, token: str) -> dict:
        """Decode a JWT token into a payload."""
        raise NotImplementedError()


class HMACJWTSerializer(HMACJWTSerializerBase):
    """JWT token encode/decode using HMAC."""

    def encode(self, payload: dict) -> str:
        """Encode a payload into a JWT token."""
        return jwt.encode(
            payload=payload,
            key=self.secret,
            algorithm=self.algorithm.value,
            json_encoder=UUIDJSONEncode,
        )

    def decode(self, token: str) -> dict:
        """Decode a JWT token into a payload."""
        try:
            return jwt.decode(
                jwt=token,
                key=self.secret,
                algorithms=[self.algorithm.value],
                issuer=self.issuer,
                audience=self.audience,
                options=self.verify_options,
            )
        except InvalidTokenError as e:
            logger.debug("Failed to decode token", exc_info=e)
            raise FailedTokenDecode from e


class BearerAuthentication(AuthenticationHandler):
    """Authentication handler for Bearer tokens with dynamic validation."""

    token_type = b"Bearer"
    header_name = b"Authorization"

    def __init__(self, serializer: HMACJWTSerializerBase):
        self.serializer = serializer

    async def authenticate(self, request: Request) -> Optional[Identity]:
        raw_token = self._get_request_token(request)
        if not raw_token:
            request.identity = Identity({})
            return None

        try:
            token = self.serializer.decode(raw_token)
            TokenPayload.parse_obj(token)
        except FailedTokenDecode:
            request.identity = Identity({})
            return None

        if token["typ"] != "access":
            request.identity = Identity({})
            return None

        request.identity = Identity(token, self.token_type.decode())

        return request.identity

    def _get_request_token(self, request: Request) -> str | None:
        auth_header = request.headers.get_first(self.header_name)
        if not auth_header:
            return None
        if auth_header.startswith(self.token_type + b" ") is False:
            return None

        try:
            token = auth_header[7:].decode()
        except UnicodeDecodeError:
            return None

        return token


class AuthProviderBase:
    """Base class for authentication storage.

    Verifies creadentials, refresh and revoke tokens.
    """

    async def authenticate(self, username: str, password: str) -> Identity:
        """Authenticate a user.

        Check if the user exists and the password is correct. Returns an identity with access and refresh tokens.
        """
        raise NotImplementedError()

    async def refresh_token(self, raw_token: str) -> Identity:
        """Verify a refresh token.

        Check if the refresh token is valid and not expired. Returns an identity with access and refresh tokens.
        """
        raise NotImplementedError()

    async def revoke_refresh_token(self, session_id: Any) -> None:
        """Revoke a refresh token.

        Remove the refresh token from the storage for a given session id.
        """
        raise NotImplementedError()


class AppAuthProvider(AuthProviderBase):
    def __init__(
        self,
        storage: UserDAL,
        serializer: HMACJWTSerializerBase,
        settings: OAuth2PasswordSettings,
    ):
        self.storage = storage
        self.serializer = serializer
        self.settings = settings

    async def authenticate(self, username: str, password: str) -> Identity:
        user = await self.storage.get_authuser_by_username(username)
        if not user:
            raise UnauthorizedException("User or password is invalid")
        if not checkpw(password, user.password):
            raise UnauthorizedException("User or password is invalid")
        if not user.active:
            raise UnauthorizedException("User or password is invalid")

        access_payload, refresh_payload = self._get_tokens_pair(user.id)
        access_token, refresh_token = self._encode_tokens(
            access_payload,
            refresh_payload,
        )
        await self._store_refresh_token(refresh_payload)

        identity = self._make_identity(access_payload, access_token, refresh_token)
        return identity

    def _make_identity(
        self, payload: TokenPayload, access_token: str, refresh_token: str
    ) -> Identity:
        identity = Identity(payload.dict())
        identity.access_token = access_token
        identity.refresh_token = refresh_token
        return identity

    def _get_tokens_pair(
        self, sub: UUID4, sid: UUID4 | None = None
    ) -> tuple[TokenPayload, TokenPayload]:
        sid = sid or uuid4()
        jti = uuid4()
        now = datetime.utcnow()
        access = TokenPayload(
            sub=sub,
            jti=jti,
            sid=sid,
            iat=now,
            nbf=now,
            exp=now + timedelta(minutes=self.settings.access_token_ttl),
            typ="access",
        )
        refresh = TokenPayload(
            sub=sub,
            jti=jti,
            sid=sid,
            iat=now,
            nbf=now,
            exp=now + timedelta(minutes=self.settings.refresh_token_ttl),
            typ="refresh",
        )
        return access, refresh

    def _encode_tokens(
        self,
        access_payload: TokenPayload,
        refresh_payload: TokenPayload,
    ) -> tuple[str, str]:
        access_token = self.serializer.encode(access_payload.dict())
        refresh_token = self.serializer.encode(refresh_payload.dict())
        return access_token, refresh_token

    async def _store_refresh_token(self, token_payload: TokenPayload) -> None:
        await self.storage.save_refresh_token(
            token_payload.sub,
            token_payload.jti,
            token_payload.sid,
            token_payload.exp,
        )

    async def _remove_used_refresh_token(self, jti: UUID4):
        await self.storage.remove_used_refresh_token(jti)

    async def refresh_token(self, raw_token: str) -> Identity:
        try:
            used_refresh_token = self.serializer.decode(raw_token)
        except FailedTokenDecode as e:
            raise UnauthorizedException(
                f"Invalid refresh token: {FailedTokenDecode}",
            ) from e

        if used_refresh_token["typ"] != "refresh":
            raise UnauthorizedException("Invalid type of refresh token")

        user = await self.storage.get_user_by_refresh_token(
            UUID(used_refresh_token["sub"]),
            UUID(used_refresh_token["jti"]),
            UUID(used_refresh_token["sid"]),
        )
        if not user:
            # someone is trying to use already used refresh token. revoke all refresh tokens for this user
            await self.revoke_refresh_token(used_refresh_token["sub"])
            raise UnauthorizedException("Invalid refresh token")

        # TODO: wrap delete old and store new refresh token to transaction
        access_payload, refresh_payload = self._get_tokens_pair(
            sub=user.id,
            sid=used_refresh_token["sid"],
        )
        access_token, refresh_token = self._encode_tokens(
            access_payload, refresh_payload
        )
        await self._store_refresh_token(refresh_payload)
        await self._remove_used_refresh_token(UUID(used_refresh_token["jti"]))
        identity = self._make_identity(access_payload, access_token, refresh_token)
        return identity

    async def revoke_refresh_token(self, user_id: str) -> None:
        await self.storage.revoke_refresh_token(UUID(user_id))


class OAuth2PasswordHandler:
    def __init__(
        self,
        *,
        settings: OAuth2PasswordSettings,
        auth_provider: AuthProviderBase,
    ):
        self.settings = settings
        self.auth_provider = auth_provider

    async def token_handler(self, request: Request) -> Response:
        """Handler for OAuth2 Password flow.

        Issue access and refresh tokens when user logs in.

        Response headers should contain:
            Cache-Control: no-store
            Pragma: no-cache
        """
        userdata = await self._fetch_credentials(request)
        identity = await self.auth_provider.authenticate(**asdict(userdata))
        if not identity:
            raise UnauthorizedException("Invalid username or password")
        return json(
            dict(
                access_token=identity.access_token,
                refresh_token=identity.refresh_token,
                token_type="Bearer",
            )
        )

    async def _fetch_credentials(self, request: Request) -> OAuth2PasswordAuthData:
        """Extract user credentials from request."""
        content_type = request.headers.get_first(b"Content-Type")
        if content_type == b"application/x-www-form-urlencoded":
            userdata = await self._form_userdata(request)
        elif content_type == b"application/json":
            userdata = await self._json_userdata(request)
        else:
            raise UnauthorizedException(
                "Unsupported Content-Type. Supported: application/x-www-form-urlencoded, application/json"
            )

        return userdata

    async def _form_userdata(self, request: Request) -> OAuth2PasswordAuthData:
        """Extract user credentials from form payload."""
        form = await request.form()
        if not form:
            raise ValueError("Cannot parse form data")
        username = form.get(self.settings.username_field, None)
        if username is None or not isinstance(username, str):
            raise ValueError("Username filed is required and must be a string")
        password = form.get(self.settings.password_field, None)
        if password is None or not isinstance(password, str):
            raise ValueError("Password filed is required and must be a string")
        return OAuth2PasswordAuthData(
            username=username,
            password=password,
        )

    async def _json_userdata(self, request: Request) -> OAuth2PasswordAuthData:
        """Extract user credentials from JSON payload."""
        data = await request.json()
        username = data.get(self.settings.username_field)
        if username is None or not isinstance(username, str):
            raise ValueError("Username filed is required and must be a string")
        password = data.get(self.settings.password_field)
        if password is None or not isinstance(password, str):
            raise ValueError("Password filed is required and must be a string")
        return OAuth2PasswordAuthData(
            username=username,
            password=password,
        )

    async def refresh_handler(self, request: Request) -> Response:
        """Handler for OAuth2 Refresh flow.

        Issue new access and refresh tokens when user make request with refresh token.

        Response headers should contain:
            Cache-Control: no-store
            Pragma: no-cache
        """
        refreshdata = await self._fetch_refresh_token(request)
        identity = await self.auth_provider.refresh_token(**asdict(refreshdata))
        if not identity:
            raise UnauthorizedException("Invalid refresh token")
        return json(
            dict(
                access_token=identity.access_token,
                refresh_token=identity.refresh_token,
                token_type="Bearer",
            )
        )

    async def _fetch_refresh_token(self, request: Request) -> OAuth2PasswordRefreshData:
        """Extract refresh token from request."""
        content_type = request.headers.get_first(b"Content-Type")
        if content_type == b"application/x-www-form-urlencoded":
            refreshdata = await self._form_refreshdata(request)
        elif content_type == b"application/json":
            refreshdata = await self._json_refreshdata(request)
        else:
            raise ValueError(
                "Unsupported Content-Type. Supported: application/x-www-form-urlencoded, application/json"
            )

        return refreshdata

    async def _form_refreshdata(self, request: Request) -> OAuth2PasswordRefreshData:
        """Extract refresh token from form payload."""
        form = await request.form()
        if not form:
            raise ValueError("Cannot parse form data")
        refresh_token = form.get("refresh_token", None)
        if refresh_token is None or not isinstance(refresh_token, str):
            raise ValueError("Refresh token filed is required and must be a string")
        return OAuth2PasswordRefreshData(
            refresh_token=refresh_token,
        )

    async def _json_refreshdata(self, request: Request) -> OAuth2PasswordRefreshData:
        """Extract refresh token from JSON payload."""
        data = await request.json()
        refresh_token = data.get("refresh_token")
        if refresh_token is None or not isinstance(refresh_token, str):
            raise ValueError("Refresh token field is required and must be a string")
        return OAuth2PasswordRefreshData(
            refresh_token=refresh_token,
        )

    async def revoke_handler(self, request: Request) -> Response:
        """Handler for revoke token.

        Revoke refresh tokens and/or access tokens during logout.
        """
        if not request.identity or request.identity.is_authenticated() is False:
            raise UnauthorizedException("Authentication required")
        session_id = request.identity["session_id"]
        if session_id is None or not isinstance(session_id, str):
            raise ValueError("Session ID filed is required and must be a string")
        await self.auth_provider.revoke_refresh_token(session_id)

        return no_content()


def use_oauth2_password(
    app: Application,
    settings: OAuth2PasswordSettings,
    auth_provider: Optional[AuthProviderBase] = None,
    auth_handler: Optional[AuthenticationHandler] = None,
    authz_policies: Optional[List[Policy]] = None,
):
    """Register OAuth2 Password handlers."""

    serializer = HMACJWTSerializer(
        secret=settings.secret,
        algorithm=settings.algorithm,
        issuer=settings.issuer,
        audience=settings.audience,
        verify_options={
            "verify_exp": True,
            "verify_iat": True,
            "verify_nbf": True,
            "verify_signature": True,
        },
    )

    auth_handler = auth_handler or BearerAuthentication(
        serializer,
    )

    authz_policies = authz_policies or [
        Policy("authenticated", AuthenticatedRequirement())
    ]

    auth_provider = auth_provider or AppAuthProvider(
        storage=UserDAL(),
        serializer=serializer,
        settings=settings,
    )
    handler = OAuth2PasswordHandler(
        settings=settings,
        auth_provider=auth_provider,
    )

    @allow_anonymous()
    @app.router.post(settings.token_path)
    @cache_control(no_cache=True, no_store=True)
    async def token_handler(request: Request):
        return await handler.token_handler(request)

    @allow_anonymous()
    @app.router.post(settings.refresh_path)
    @cache_control(no_cache=True, no_store=True)
    async def refresh_handler(request: Request):
        return await handler.refresh_handler(request)

    @app.router.get(settings.revoke_path)
    @cache_control(no_cache=True, no_store=True)
    async def revoke_handler(request: Request):
        return await handler.revoke_handler(request)

    authentication = app.use_authentication()
    authentication.add(auth_handler)

    authorization = app.use_authorization()
    for policy in authz_policies:
        authorization.add(policy)
