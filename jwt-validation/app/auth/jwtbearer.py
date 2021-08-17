import logging
from typing import Optional, Sequence

from blacksheep.messages import Request
from guardpost.asynchronous.authentication import AuthenticationHandler
from guardpost.authentication import Identity, User
from jwt.exceptions import InvalidTokenError

from core.jwts import InvalidAuthorizationToken, JWTValidator


def get_logger():
    return logging.getLogger("auth-jwt-bearer")


class JWTBearerAuthentication(AuthenticationHandler):
    """Identifies a user from a JWT Bearer access token."""

    def __init__(
        self,
        *,
        authority: str,
        valid_issuers: Sequence[str],
        valid_audiences: Sequence[str],
        header_name: str = "Authorization",
    ):
        self.header_name = header_name
        self.logger = get_logger()

        self._validator = JWTValidator(
            authority=authority,
            valid_issuers=valid_issuers,
            valid_audiences=valid_audiences,
        )

    async def authenticate(self, context: Request) -> Optional[Identity]:
        authorization_value = context.get_first_header(b"Authorization")

        if not authorization_value:
            context.identity = User({})
            return None

        if not authorization_value.startswith(b"Bearer "):
            self.logger.debug(
                "Invalid Authorization header, not starting with `Bearer ` "
                "the header is ignored."
            )
            context.identity = User({})
            return None

        token = authorization_value[7:].decode()

        try:
            decoded = await self._validator.validate_jwt(token)
        except (InvalidAuthorizationToken, InvalidTokenError) as ex:
            # pass, because the application might support more than one
            # authentication method
            self.logger.error("JWT Bearer - invalid access token: %s", str(ex))
            pass
        else:
            context.identity = User(decoded, "JWT Bearer")
            return context.identity

        context.identity = User({})
        return None
