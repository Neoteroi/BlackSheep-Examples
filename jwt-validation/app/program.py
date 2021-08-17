from blacksheep.server import Application
from configuration.common import Configuration
from rodi import Container
from service.settings import Settings

from .auth import configure_auth
from .controllers.home import HomeController  # NoQA


def configure_application(
    services: Container,
    configuration: Configuration,
    settings: Settings,
) -> Application:
    app = Application(
        services=services,
        show_error_details=configuration.show_error_details,
        debug=configuration.debug,
    )

    configure_auth(app, settings)

    return app
