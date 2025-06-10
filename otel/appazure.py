"""
Basic OTEL example with Azure Application Insights.
"""

import logging
import os
import weakref
from functools import wraps

from azure.monitor.opentelemetry.exporter import (
    AzureMonitorLogExporter,
    AzureMonitorTraceExporter,
)
from blacksheep import Application, Request, Response, text
from opentelemetry import trace
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import SpanKind

# Set your Azure Application Insights connection string here
connection_string = "******"

os.environ["OTEL_RESOURCE_ATTRIBUTES"] = (
    "service.name=learning-app,service.namespace=learning,deployment.environment=local"
)

# Configure logging
log_exporter = AzureMonitorLogExporter(connection_string=connection_string)
log_provider = LoggerProvider()
log_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
logging.setLoggerClass(logging.getLoggerClass())
logging.getLogger("opentelemetry").setLevel(logging.WARNING)
otel_handler = LoggingHandler(level=logging.NOTSET, logger_provider=log_provider)
logging.getLogger().addHandler(otel_handler)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s] %(message)s",
)
logger = logging.getLogger(__name__)

LoggingInstrumentor().instrument(set_logging_format=True)

# Set up the tracer provider and Azure Monitor trace exporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
span_processor = BatchSpanProcessor(
    AzureMonitorTraceExporter(connection_string=connection_string)
)
trace.get_tracer_provider().add_span_processor(span_processor)  # type: ignore


class OTELApplication(Application):
    requests_spans = weakref.WeakKeyDictionary()

    async def handle(self, request: Request) -> Response:
        tracer = trace.get_tracer(__name__)
        path = request.url.path.decode("utf8")
        method = request.method
        with tracer.start_as_current_span(
            f"{method} {path}", kind=SpanKind.SERVER
        ) as span:
            self.requests_spans[request] = span
            response = await super().handle(request)

            # Optional: to reduce cardinality, update the span name with the now
            # available route that matched the request (if any)
            route = request.route  # type: ignore
            span.update_name(f"{method} {route}")

            span.set_attribute("http.status_code", response.status)
            span.set_attribute("http.method", request.method)
            span.set_attribute("http.path", path)
            span.set_attribute("http.url", request.url.value.decode())
            span.set_attribute("http.route", route)
            span.set_attribute("http.status_code", response.status)
            span.set_attribute("client.ip", request.original_client_ip)

            # TODO: mark as error also other HTTP status codes as desired
            if response.status >= 500:
                span.set_status(trace.Status(trace.StatusCode.ERROR))

            return response

    async def handle_internal_server_error(
        self, request: Request, exc: Exception
    ) -> Response:
        """
        Handle an unhandled exception. If an exception handler is defined for
        InternalServerError or status 500, it is used.
        """
        span = self.requests_spans.get(request)
        if span is not None:
            span.record_exception(exc)
            span.set_status(trace.Status(trace.StatusCode.ERROR))

        return await super().handle_internal_server_error(request, exc)


# Usage example:
app = OTELApplication()


@app.on_start
async def on_start(app):
    # Patch the router to keep track of the route pattern that matched the request, if
    # any
    # https://www.neoteroi.dev/blacksheep/routing/#how-to-track-routes-that-matched-a-request
    def wrap_get_route_match(fn):
        @wraps(fn)
        def get_route_match(request):
            match = fn(request)
            request.route = match.pattern.decode() if match else "Not Found"  # type: ignore
            return match

        return get_route_match

    app.router.get_match = wrap_get_route_match(app.router.get_match)  # type: ignore


# Add this to your BlackSheep app setup
@app.on_stop
async def on_stop(app):
    pass  # Remove shutdown call if not supported


@app.router.get("/")
async def home(request) -> Response:
    # logger.warning appear in the traces table
    logger.warning("Example warning")
    return text("Hello, traced BlackSheep!")


@app.router.get("/{name}")
async def greetings(name: str) -> Response:
    return text(f"Hello, {name}!")


@app.router.get("/crash")
async def crash_test() -> Response:
    raise RuntimeError("Crash test")
