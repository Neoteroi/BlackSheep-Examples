import json
import os

from blacksheep.server.application import Application
from blacksheep.server.authentication.jwt import JWTBearerAuthentication
from blacksheep.server.responses import html
from dotenv import load_dotenv
from guardpost.authentication import Identity
from guardpost.authorization import Policy
from guardpost.common import AuthenticatedRequirement

# read .env file into environment variables
load_dotenv()

app = Application()

aad_authority = os.environ["API_ISSUER"]
api_audience = os.environ["API_AUDIENCE"]


# configure the application to support authentication using JWT access tokens obtained
# from "Authorization: Bearer {...}" request headers;
# access tokens are validated using OpenID Connect configuration from the configured
# authority
app.use_authentication().add(
    JWTBearerAuthentication(
        authority=aad_authority,
        valid_audiences=[api_audience],
    )
)

# configure authorization with a default policy that requires an authenticated user for
# all endpoints, except when request handlers are explicitly decorated by
# @allow_anonymous
app.use_authorization().with_default_policy(
    Policy("authenticated", AuthenticatedRequirement())
)

get = app.router.get


@get("/")
def home(user: Identity):
    assert user.is_authenticated()

    return html(
        f"""
<!DOCTYPE html>
<html>
<head>
<style>
pre {{
    border: 1px dotted darkred;
    padding: 1rem;
}}
</style>
</head>
<body>
    <h1>Welcome! These are your claims:</h1>
    <pre>{json.dumps(user.claims, ensure_ascii=False, indent=4)}</pre>
</body>
</html>
"""
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="debug")
