"""
This module provides classes and functions to work with OpenTelemetry.
"""

import logging
import os
from contextlib import contextmanager
from functools import wraps
from typing import Dict

from blacksheep import Application
from blacksheep.messages import Request
from blacksheep.server.env import get_env
from opentelemetry import trace
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, LogExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter
from opentelemetry.trace import SpanKind


class OTELMiddleware:
    """
    Middleware configuring OpenTelemetry for all web requests.
    """

    def __init__(self, exc_handler, tracer_name: str | None = None) -> None:
        self._exc_handler = exc_handler
        self._tracer = trace.get_tracer(tracer_name or __name__)

    async def __call__(self, request: Request, handler):
        path = request.url.path.decode("utf8")
        method = request.method
        with self._tracer.start_as_current_span(
            f"{method} {path}", kind=SpanKind.SERVER
        ) as span:
            try:
                response = await handler(request)
            except Exception as exc:
                response = await self._exc_handler(request, exc)

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

            if response.status >= 400:
                span.set_status(trace.Status(trace.StatusCode.ERROR))

            return response


def _configure_logging(log_exporter: LogExporter, span_exporter: SpanExporter):
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

    LoggingInstrumentor().instrument(set_logging_format=True)

    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(span_exporter))  # type: ignore


def set_attributes(
    service_name: str,
    service_namespace: str = "default",
    env: str = "",
):
    """
    Sets the OTEL_RESOURCE_ATTRIBUTES environment variable with service metadata
    for OpenTelemetry.

    Args:
        service_name (str): The name of the service.
        service_namespace (str, optional): The namespace of the service. Defaults to "default".
        env (str, optional): The deployment environment. If not provided, it is determined from the environment.

    Returns:
        None
    """
    if not env:
        env = get_env()
    os.environ["OTEL_RESOURCE_ATTRIBUTES"] = (
        f"service.name={service_name},"
        f"service.namespace={service_namespace},"
        f"deployment.environment={env}"
    )


def use_open_telemetry(
    app: Application,
    log_exporter: LogExporter,
    span_exporter: SpanExporter,
):
    if os.getenv("OTEL_RESOURCE_ATTRIBUTES") is None:
        # set a default value
        set_attributes("blacksheep-app")

    _configure_logging(log_exporter, span_exporter)

    app.middlewares.append(OTELMiddleware(app.handle_request_handler_exception))

    @app.on_start
    async def on_start(app):
        # Patch the router to keep track of the route pattern that matched the request,
        # if any
        # https://www.neoteroi.dev/blacksheep/routing/#how-to-track-routes-that-matched-a-request
        def wrap_get_route_match(fn):
            @wraps(fn)
            def get_route_match(request):
                match = fn(request)
                request.route = match.pattern.decode() if match else "Not Found"  # type: ignore
                return match

            return get_route_match

        app.router.get_match = wrap_get_route_match(app.router.get_match)  # type: ignore


@contextmanager
def client_span_context(
    operation_name: str, attributes: Dict[str, str], *args, **kwargs
):
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span(operation_name, kind=SpanKind.CLIENT) as span:
        span.set_attributes(attributes)
        for i, value in enumerate(args):
            span.set_attribute(f"@arg{i}", str(value))
        for key, value in kwargs.items():
            span.set_attribute(f"@{key}", str(value))
        try:
            yield
        except Exception as ex:
            span.record_exception(ex)
            span.set_attribute("ERROR", str(ex))
            span.set_attribute("http.status_code", 500)
            span.set_status(trace.Status(trace.StatusCode.ERROR))
            raise


def logcall(component="Service"):
    """
    Wraps a function to log each call using OpenTelemetry.
    """

    def log_decorator(fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            with client_span_context(
                fn.__name__, {"component": component}, *args, **kwargs
            ):
                return await fn(*args, **kwargs)

        return wrapper

    return log_decorator
