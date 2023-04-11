"""
This example shows how to configure an OpenID Connect integration having tokens
exchanged with the client using the HTML5 Storage API, instead of response cookies.
This scenario enables better reusability of web APIs.
See how the id_token is used in ./static/index.html to authenticate following requests
('Authorization: Bearer ***' headers), and how the refresh token endpoint can be used
to obtain fresh tokens.
"""
import uvicorn
from blacksheep.server.application import Application
from blacksheep.server.authentication.jwt import JWTBearerAuthentication
from blacksheep.server.authentication.oidc import (
    JWTOpenIDTokensHandler,
    OpenIDSettings,
    use_openid_connect,
)
from dotenv import load_dotenv

from common.routes import register_routes
from common.secrets import Secrets

load_dotenv()
secrets = Secrets.from_env()
app = Application(show_error_details=True)


AUTHORITY = (
    "https://login.microsoftonline.com/b62b317a-19c2-40c0-8650-2d9672324ac4/v2.0"
)
CLIENT_ID = "499adb65-5e26-459e-bc35-b3e1b5f71a9d"
use_openid_connect(
    app,
    OpenIDSettings(
        authority=AUTHORITY,
        client_id=CLIENT_ID,
        client_secret=secrets.aad_client_secret,
        scope=(
            "openid profile offline_access email "
            "api://65d21481-4f1a-4731-9508-ad965cb4d59f/example"
        ),
    ),
    auth_handler=JWTOpenIDTokensHandler(
        JWTBearerAuthentication(
            authority=AUTHORITY,
            valid_audiences=[CLIENT_ID],
        ),
    ),
)

register_routes(app, static_home=True)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="debug")
