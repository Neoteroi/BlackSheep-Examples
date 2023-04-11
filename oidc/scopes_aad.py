"""
This example shows how to configure an OpenID Connect integration with Azure Active
Directory, obtaining an id_token, an access_token, and a refresh_token. The id_token
is exchanged with the client using a response cookie (also used to authenticate users
for following requests), while the access token and the refresh token are stored using
a custom implementation of TokensStore.
"""
from datetime import datetime

import uvicorn
from blacksheep import Request, Response
from blacksheep.server.application import Application
from blacksheep.server.authentication.oidc import (
    CookiesOpenIDTokensHandler,
    OpenIDSettings,
    TokensStore,
    use_openid_connect,
)
from dotenv import load_dotenv

from common.routes import register_routes
from common.secrets import Secrets

load_dotenv()
secrets = Secrets.from_env()
app = Application(show_error_details=True)


class TestTokensStore(TokensStore):
    def __init__(self) -> None:
        super().__init__()
        self._access_token: str | None = None
        self._refresh_token: str | None = None

    async def store_tokens(
        self,
        request: Request,
        response: Response,
        access_token: str,
        refresh_token: str | None,
        expires: datetime | None = None,
    ):
        """
        Applies a strategy to store an access token and an optional refresh token for
        the given request and response.
        """
        self._access_token = access_token
        self._refresh_token = refresh_token

    async def unset_tokens(self, request: Request):
        """
        Optional method, to unset access tokens upon sign-out.
        """
        self._access_token = None
        self._refresh_token = None

    async def restore_tokens(self, request: Request) -> None:
        """
        Applies a strategy to restore an access token and an optional refresh token for
        the given request.
        """
        assert request.identity is not None
        request.identity.access_token = self._access_token
        request.identity.refresh_token = self._refresh_token


# AAD with custom scope
handler = use_openid_connect(
    app,
    OpenIDSettings(
        authority="https://login.microsoftonline.com/b62b317a-19c2-40c0-8650-2d9672324ac4/v2.0/",
        client_id="499adb65-5e26-459e-bc35-b3e1b5f71a9d",
        client_secret=secrets.aad_client_secret,
        scope="openid profile offline_access email "
        "api://65d21481-4f1a-4731-9508-ad965cb4d59f/example",
    ),
)

assert isinstance(handler.auth_handler, CookiesOpenIDTokensHandler)
handler.auth_handler.tokens_store = TestTokensStore()

register_routes(app)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="debug")
