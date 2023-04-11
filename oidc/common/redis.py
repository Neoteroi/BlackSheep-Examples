import logging
from datetime import datetime
from json import JSONDecodeError, dumps, loads
from typing import Optional
from uuid import uuid4

import redis.asyncio as redis
from blacksheep import Cookie, Request, Response
from blacksheep.server.authentication.oidc import TokensStore, logger
from guardpost import Identity

logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class RedisTokensStore(TokensStore):
    """
    A tokens store that can stores access tokens and refresh tokens using Redis,
    with the given `redis.asyncio.redis` client. This tokens store configures a trace_id
    """

    def __init__(
        self,
        client: redis.Redis,
        trace_cookie_name: str = "tokenstraceid",
        expiration_seconds: int = 60 * 120,
    ) -> None:
        super().__init__()
        self._client = client
        self._trace_id_cookie_name = trace_cookie_name
        self._expiration_seconds = expiration_seconds

    def get_trace_id(self, request: Request) -> str:
        trace_id = request.cookies.get(self._trace_id_cookie_name)

        if trace_id:
            return trace_id
        return str(uuid4())

    def set_cookie(
        self,
        response: Response,
        cookie_name: str,
        value: str,
        secure: bool,
        expires: Optional[datetime] = None,
        path: str = "/",
    ) -> None:
        response.set_cookie(
            Cookie(
                cookie_name,
                value,
                domain=None,
                path=path,
                http_only=True,
                secure=secure,
                expires=expires,
            )
        )

    async def store_tokens(
        self,
        request: Request,
        response: Response,
        access_token: str,
        refresh_token: str | None,
    ):
        """
        Applies a strategy to store an access token and an optional refresh token for
        the given request and response.
        """
        trace_id = self.get_trace_id(request)
        secure = request.scheme == "https"
        self.set_cookie(
            response,
            self._trace_id_cookie_name,
            trace_id,
            secure=secure,
            expires=None,
        )
        await self._client.set(
            trace_id,
            dumps({"access_token": access_token, "refresh_token": refresh_token}),
            ex=self._expiration_seconds,
        )

    async def restore_tokens(self, request: Request) -> None:
        """
        Applies a strategy to restore an access token and an optional refresh token for
        the given request.
        """
        trace_id = request.cookies.get(self._trace_id_cookie_name)

        if not trace_id:
            return

        value = await self._client.get(trace_id)
        if not value:
            return

        try:
            data = loads(value)
        except JSONDecodeError as json_error:
            logger.debug(
                "Ignoring tokens because the cached value cannot be parsed. "
                "Trace id %s",
                trace_id,
                exc_info=json_error,
            )
        else:
            if request.identity is None:
                request.identity = Identity({})
            request.identity.access_token = data.get("access_token")
            request.identity.refresh_token = data.get("refresh_token")

    async def unset_tokens(self, request: Request):
        """
        Unsets access tokens upon sign-out.
        """
        cookie = request.cookies.get(self._trace_id_cookie_name)

        if cookie:
            await self._client.delete(cookie)
