import os

from blacksheep import Application
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

from . import use_open_telemetry


def use_open_telemetry_otlp(
    app: Application,
    service_name: str = "unknown",
    service_namespace: str = "default",
    env: str = "",
):
    """
    Configures OpenTelemetry for a BlackSheep application using OTLP exporters.

    This function checks for required OTLP-related environment variables and sets up
    OpenTelemetry logging and tracing using OTLPLogExporter and OTLPSpanExporter.

    Args:
        app: The BlackSheep Application instance.
        service_name: The name of the service (default: "unknown").
        service_namespace: The namespace of the service (default: "default").
        env: The deployment environment (default: "").

    Raises:
        ValueError: If any required OTLP environment variables are missing.
    """
    expected_vars = [
        "OTEL_RESOURCE_ATTRIBUTES",
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "OTEL_EXPORTER_OTLP_HEADERS",
        "OTEL_EXPORTER_OTLP_PROTOCOL",
    ]
    missing_vars = [var for var in expected_vars if os.environ.get(var) is None]
    if missing_vars:
        raise ValueError(f"Missing env variables: {', '.join(missing_vars)}")

    # Uses environment variables for configuration
    use_open_telemetry(
        app,
        OTLPLogExporter(),
        OTLPSpanExporter(),
        service_name,
        service_namespace,
        env,
    )
