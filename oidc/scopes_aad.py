import uvicorn
from blacksheep.server.application import Application
from blacksheep.server.authentication.oidc import (
    OpenIDSettings,
    use_openid_connect,
    CookiesTokensStore,
)
from dotenv import load_dotenv

from common.routes import register_routes
from common.secrets import Secrets

load_dotenv()
secrets = Secrets.from_env()
app = Application(show_error_details=True)


# AAD with custom scope
use_openid_connect(
    app,
    OpenIDSettings(
        authority="https://login.microsoftonline.com/a2884dee-52e8-4034-8ce2-6b48e18d1ae7/v2.0/",
        client_id="067cee45-faf3-4c75-9fef-09f050bcc3ae",
        client_secret=secrets.aad_client_secret,
        scope="openid profile email api://0ed1cebe-b7ca-45c5-a4bf-a8d586c18d31/read:todos",
    ),
    tokens_store=CookiesTokensStore(),
)

register_routes(app)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="debug")
