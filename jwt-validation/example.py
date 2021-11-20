from blacksheep.server.application import Application
from blacksheep.server.authentication.jwt import JWTBearerAuthentication
from blacksheep.server.authorization import auth
from guardpost.common import AuthenticatedRequirement, Policy

app = Application()


app.use_authentication().add(
    JWTBearerAuthentication(
        authority="https://login.microsoftonline.com/robertoprevatogmail.onmicrosoft.com",
        valid_audiences=["104bca60-c5a7-4ab9-83e1-7b9c8dad71e2"],
        valid_issuers=[
            "https://login.microsoftonline.com/b62b317a-19c2-40c0-8650-2d9672324ac4/v2.0"
        ],
    )
)

authorization = app.use_authorization()

authorization += Policy("any_name", AuthenticatedRequirement())

get = app.router.get


@get("/")
def home():
    return "Hello, World"


@auth("any_name")
@get("/api/message")
def example():
    return "This is only for authenticated users"
