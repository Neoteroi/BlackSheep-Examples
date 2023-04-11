"""
This example shows how to configure an OpenID Connect integration with Azure Active
Directory, obtaining only an id_token, exchanged with the client using a response
cookie.
"""
import uvicorn
from blacksheep.server.application import Application
from blacksheep.server.authentication.oidc import OpenIDSettings, use_openid_connect

from common.routes import register_routes

app = Application(show_error_details=True)


# basic AAD integration that handles only an id_token
use_openid_connect(
    app,
    OpenIDSettings(
        authority="https://login.microsoftonline.com/b62b317a-19c2-40c0-8650-2d9672324ac4/v2.0/",
        client_id="499adb65-5e26-459e-bc35-b3e1b5f71a9d",
    ),
)

register_routes(app)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="debug")
