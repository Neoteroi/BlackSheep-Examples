import asyncio
import logging
import os

from blacksheep import Application, HTTPException, Response, json, text
from dotenv import load_dotenv

from otel import logcall
from otel.otlp import use_open_telemetry_otlp

load_dotenv(".envgrafana")

os.environ["OTEL_RESOURCE_ATTRIBUTES"] = (
    "service.name=learning-app2,service.namespace=learning2,deployment.environment=local"
)

app = Application()

use_open_telemetry_otlp(app)


logger = logging.getLogger(__name__)


class CustomException(HTTPException):
    def __init__(self):
        super().__init__(400, "Something wrong!")


@app.exception_handler(CustomException)
async def handler_example(app, request, exc: CustomException):
    return json({"message": "Oh, no! " + str(exc)}, 400)


@logcall("Example")
async def dependency_example():
    await asyncio.sleep(0.1)


@app.router.get("/")
async def home(request) -> Response:
    # logger.warning appear in the traces table
    logger.warning("Example warning")
    await dependency_example()
    return text("Hello, traced BlackSheep!")


@app.router.get("/{name}")
async def greetings(name: str) -> Response:
    return text(f"Hello, {name}!")


@app.router.get("/bad-request")
async def bad_request():
    raise CustomException()


@app.router.get("/crash")
async def crash_test() -> Response:
    raise RuntimeError("Crash test")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=44777)
