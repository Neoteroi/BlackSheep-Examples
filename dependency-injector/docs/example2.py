from typing import Type, TypeVar, get_type_hints

from dependency_injector import containers, providers

from blacksheep import Application, get

T = TypeVar("T")


class APIClient: ...


class SomeService:

    def __init__(self, api_client: APIClient) -> None:
        self.api_client = api_client


# Define the Dependency Injector container
class AppContainer(containers.DeclarativeContainer):
    api_client = providers.Singleton(APIClient)
    some_service = providers.Factory(SomeService, api_client=api_client)


# Create the container instance
container = AppContainer()


class DependencyInjectorConnector:
    """
    This class connects a Dependency Injector container with a
    BlackSheep application.
    Dependencies are registered using the code API offered by
    Dependency Injector. The BlackSheep application activates services
    using the container when needed.
    """

    def __init__(self, container: containers.Container) -> None:
        self._container = container

    def register(self, obj_type: Type[T]) -> None:
        """
        Registers a type with the container.
        The code below inspects the object's constructor's types annotations to
        automatically configure the provider to activate the type.

        It is not necessary to use @inject or Provide core on the __init__ method. This
        helps reducing code verbosity and keeping the source code not polluted by DI
        specific code.
        """
        constructor = getattr(obj_type, "__init__", None)

        if not constructor:
            raise ValueError(
                f"Type {obj_type.__name__} does not have an __init__ method."
            )

        # Get the type hints for the constructor parameters
        type_hints = get_type_hints(constructor)

        # Exclude 'self' from the parameters
        dependencies = {
            param_name: getattr(self._container, self._get_provider_name(param_type))
            for param_name, param_type in type_hints.items()
            if param_name not in {"self", "return"}
            and hasattr(self._container, self._get_provider_name(param_type))
        }

        # Create a provider for the type with its dependencies
        provider = providers.Factory(obj_type, **dependencies)
        setattr(self._container, self._get_provider_name(obj_type), provider)

    def resolve(self, obj_type: Type[T], _) -> T:
        """Resolves an instance of the given type."""
        provider = getattr(self._container, self._get_provider_name(obj_type), None)
        if provider is None:
            raise TypeError(
                f"Type {obj_type.__name__} is not registered in the container."
            )
        return provider()

    def __contains__(self, item: Type[T]) -> bool:
        """Checks if a type is registered in the container."""
        return hasattr(self._container, item.__name__)

    def _get_provider_name(self, obj_type) -> str:
        """
        Gets a provider name by object type.
        """
        return self._to_snake_case(obj_type.__name__)

    def _to_snake_case(self, name: str) -> str:
        """
        Converts a PascalCase or camelCase string to snake_case.

        Args:
            name (str): The string to convert.

        Returns:
            str: The converted string in snake_case.
        """
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


app = Application(
    services=DependencyInjectorConnector(container), show_error_details=True
)


@get("/")
def home(service: SomeService):
    print(service)
    # DependencyInjector resolved the dependencies
    assert isinstance(service, SomeService)
    assert isinstance(service.api_client, APIClient)
    return id(service)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=44777)
