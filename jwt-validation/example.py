from blacksheep.server import Application
from blacksheep.server.authorization import auth
from configuration.common import ConfigurationBuilder
from configuration.json import JSONFile
from guardpost.common import AuthenticatedRequirement, Policy

from app.auth.jwtbearer import JWTBearerAuthentication

# read application settings from a configuration file
config_builder = ConfigurationBuilder(JSONFile("settings.json"))
config = config_builder.build()


app = Application(show_error_details=config.show_error_details)


app.use_authentication().add(
    JWTBearerAuthentication(
        authority=config.auth.authority,
        valid_audiences=[config.auth.client_id],
        valid_issuers=config.auth.valid_issuers,
    )
)

authorization = app.use_authorization()

authorization += Policy("authenticated", AuthenticatedRequirement())

get = app.router.get


@get("/")
def home():
    return "Hello, World"


@auth("authenticated")
@get("/api/message")
def example():
    return "This is only for authenticated users"
