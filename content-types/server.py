from dataclasses import dataclass

from blacksheep import Application, get, post, FromJSON, FromXML
from blacksheep.server.openapi.v3 import OpenAPIHandler
from openapidocs.v3 import Info

app = Application()

docs = OpenAPIHandler(info=Info(title="Example API", version="0.0.1"))
docs.bind_app(app)


@dataclass
class Foo:
    foo: str


@dataclass
class CreateFooInput:
    foo: str


@get("/foo")
async def get_foo() -> Foo:
    return Foo("Hello!")


@post("/foo")
async def create_foo(data: FromJSON[CreateFooInput] | FromXML[CreateFooInput]):
    return Foo(data.foo)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
