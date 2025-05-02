from typing import Type, TypeVar, get_type_hints

from dependency_injector import containers, providers

T = TypeVar("T")


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
            param_name: getattr(self._container, param_type.__name__)
            for param_name, param_type in type_hints.items()
            if param_name not in {"self", "return"}
            and hasattr(self._container, param_type.__name__)
        }

        # Create a provider for the type with its dependencies
        provider = providers.Factory(obj_type, **dependencies)
        setattr(self._container, obj_type.__name__, provider)

    def resolve(self, obj_type: Type[T], _) -> T:
        """Resolves an instance of the given type."""
        provider = getattr(self._container, obj_type.__name__, None)
        if provider is None:
            raise TypeError(
                f"Type {obj_type.__name__} is not registered in the container."
            )
        return provider()

    def __contains__(self, item: Type[T]) -> bool:
        """Checks if a type is registered in the container."""
        return hasattr(self._container, item.__name__)
