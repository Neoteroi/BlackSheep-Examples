"""
This example shows how to configure an OpenID Connect integration to obtain only an
id_token, and having it exchanged with the client using the HTML5 Storage API, instead
of a response cookie. This scenario enables better reusability of web APIs.
See how the id_token is used in ./static/index.html to authenticate following requests
('Authorization: Bearer ***' headers).
"""
import uvicorn
from blacksheep.server.application import Application
from blacksheep.server.authentication.jwt import JWTBearerAuthentication
from blacksheep.server.authentication.oidc import (
    JWTOpenIDTokensHandler,
    OpenIDSettings,
    use_openid_connect,
)

from common.routes import register_routes

app = Application(show_error_details=True)

# Basic AAD integration that handles only an id_token.
# In this case, the back-end authenticates users using id_tokens.
# Another possible scenario is to obtain both an id_token and an access_token in the
# UI (front-end and back-end are represented by distinct app registrations in the IDP);
# thus requiring access tokens for an API (this is the generally recommended approach).
AUTHORITY = "https://accounts.google.com"
CLIENT_ID = "349036756498-715barque0aq00qplb3fon9i6hig7ib9.apps.googleusercontent.com"

use_openid_connect(
    app,
    OpenIDSettings(
        authority=AUTHORITY,
        client_id=CLIENT_ID,
        callback_path="/authorization-callback",
    ),
    auth_handler=JWTOpenIDTokensHandler(
        JWTBearerAuthentication(
            authority=AUTHORITY,
            valid_audiences=[CLIENT_ID],
        )
    ),
)

register_routes(app, static_home=True)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="debug")
