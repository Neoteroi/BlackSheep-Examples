"""
This example shows how to configure an OpenID Connect integration with Okta, obtaining
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


# Okta with custom scope
use_openid_connect(
    app,
    OpenIDSettings(
        discovery_endpoint="https://dev-34685660.okta.com/oauth2/default/.well-known/oauth-authorization-server",
        client_id="0oa2gy88qiVyuOClI5d7",
        client_secret=secrets.okta_client_secret,
        callback_path="/authorization-code/callback",
        scope="openid read:todos",
    ),
)

register_routes(app)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="debug")
