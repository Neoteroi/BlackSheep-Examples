import uvicorn
from blacksheep.server.application import Application
from blacksheep.server.authentication.oidc import (
    OpenIDSettings,
    use_openid_connect,
    CookiesTokensStore,
)

from common.routes import register_routes

app = Application(show_error_details=True)


# basic Okta integration that handles only an id_token
use_openid_connect(
    app,
    OpenIDSettings(
        authority="https://dev-34685660.okta.com",
        client_id="0oa2gy88qiVyuOClI5d7",
        callback_path="/authorization-code/callback",
    ),
    tokens_store=CookiesTokensStore(),
)

register_routes(app)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="debug")
