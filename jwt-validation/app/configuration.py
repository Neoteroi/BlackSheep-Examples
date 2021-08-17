from configuration.common import Configuration, ConfigurationBuilder
from configuration.env import EnvironmentVariables
from configuration.json import JSONFile


def load_configuration() -> Configuration:
    builder = ConfigurationBuilder(
        JSONFile("settings.json"), EnvironmentVariables("APPSETTING_")
    )

    return builder.build()
