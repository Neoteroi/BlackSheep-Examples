"""
This example shows how to configure an OpenID Connect integration with Auth0, obtaining
only an id_token, exchanged with the client using a response cookie.
"""
import uvicorn
from blacksheep.server.application import Application
from blacksheep.server.authentication.oidc import (
    OpenIDSettings,
    use_openid_connect,
)

from common.routes import register_routes

app = Application(show_error_details=True)


# basic Auth0 integration that handles only an id_token
use_openid_connect(
    app,
    OpenIDSettings(
        authority="https://neoteroi.eu.auth0.com",
        client_id="OOGPl4dgG7qKsm2IOWq72QhXV4wsLhbQ",
        callback_path="/signin-oidc",
    ),
)

register_routes(app)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="debug")
