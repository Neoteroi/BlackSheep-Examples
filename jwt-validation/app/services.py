"""
Use this module to register services that are required by request handlers.
Services registered inside a `rodi.Container` are automatically injected into request
handlers.

For more information and documentation, see:
    https://www.neoteroi.dev/blacksheep/dependency-injection/
"""
from typing import Tuple

from rodi import Container
from service.settings import Settings

from configuration.common import Configuration


def configure_services(
    configuration: Configuration,
) -> Tuple[Container, Configuration, Settings]:
    container = Container()

    container.add_instance(configuration)

    settings = Settings.from_configuration(configuration)

    container.add_instance(settings)

    return container, configuration, settings
