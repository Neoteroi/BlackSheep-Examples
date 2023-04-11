"""
This example shows how to configure an OpenID Connect integration with Auth0, obtaining
an id_token, an access_token, and a refresh_token. The id_token is exchanged with the
client using a response cookie (also used to authenticate users
for following requests), while access token and the refresh token are not stored and
can only be accessed using optional events.
"""
import uvicorn
from blacksheep.server.application import Application
from blacksheep.server.authentication.oidc import OpenIDSettings, use_openid_connect
from dotenv import load_dotenv

from common.routes import register_routes
from common.secrets import Secrets

load_dotenv()
secrets = Secrets.from_env()
app = Application(show_error_details=True)


# Auth0 with custom scope
use_openid_connect(
    app,
    OpenIDSettings(
        authority="https://neoteroi.eu.auth0.com",
        audience="http://localhost:5000/api/todos",
        client_id="OOGPl4dgG7qKsm2IOWq72QhXV4wsLhbQ",
        client_secret=secrets.auth0_client_secret,
        callback_path="/signin-oidc",
        scope="openid profile read:todos",
        error_redirect_path="/sign-in-error",
    ),
)

register_routes(app)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="debug")
