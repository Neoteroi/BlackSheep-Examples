from blacksheep import Application, get
from blacksheep.server.controllers import Controller
from dependency_injector import containers, providers

from app.di import DependencyInjectorConnector


class APIClient: ...


class SomeService:

    def __init__(self, api_client: APIClient) -> None:
        self.api_client = api_client


class AnotherService: ...


# Define the Dependency Injector container
class AppContainer(containers.DeclarativeContainer):
    APIClient = providers.Singleton(APIClient)
    SomeService = providers.Factory(SomeService, api_client=APIClient)
    AnotherService = providers.Factory(AnotherService)


# Create the container instance
container = AppContainer()


app = Application(
    services=DependencyInjectorConnector(container), show_error_details=True
)


@get("/")
def home(service: SomeService):
    # DependencyInjector resolved the dependencies
    assert isinstance(service, SomeService)
    assert isinstance(service.api_client, APIClient)
    return id(service)


class TestController(Controller):

    def __init__(self, another_dep: AnotherService) -> None:
        super().__init__()
        self._another_dep = (
            another_dep  # another_dep is resolved by Dependency Injector
        )

    @app.controllers_router.get("/controller-test")
    def controller_test(self, service: SomeService):
        # DependencyInjector resolved the dependencies
        assert isinstance(self._another_dep, AnotherService)

        assert isinstance(service, SomeService)
        assert isinstance(service.api_client, APIClient)
        return id(service)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=44777)
