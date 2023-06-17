"""
This example shows how to configure an OpenID Connect integration with Google, obtaining
only an id_token, exchanged with the client using a response cookie.
"""
import uvicorn
from blacksheep.server.application import Application
from blacksheep.server.authentication.oidc import OpenIDSettings, use_openid_connect

from common.routes import register_routes

app = Application(show_error_details=True)

client_id = "349036756498-715barque0aq00qplb3fon9i6hig7ib9.apps.googleusercontent.com"

# basic Google integration that handles only an id_token
use_openid_connect(
    app,
    OpenIDSettings(
        authority="https://accounts.google.com",
        client_id=client_id,
        callback_path="/authorization-callback",
    ),
)

register_routes(app)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="debug")
