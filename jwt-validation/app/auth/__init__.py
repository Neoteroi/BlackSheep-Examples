from blacksheep.server import Application
from guardpost.common import AuthenticatedRequirement, Policy
from service.settings import Settings

from .jwtbearer import JWTBearerAuthentication


def configure_auth(app: Application, settings: Settings) -> None:
    app.use_authentication().add(
        JWTBearerAuthentication(
            authority=settings.auth.authority,
            valid_audiences=[settings.auth.client_id],
            valid_issuers=settings.auth.valid_issuers,
        )
    )

    authorization = app.use_authorization()

    authorization += Policy("authenticated", AuthenticatedRequirement())
