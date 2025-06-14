"""
This module provides integration for OpenTelemetry using OTLP (OpenTelemetry Protocol) exporters
for logging and tracing in BlackSheep applications.

It defines a helper function to configure OpenTelemetry with OTLPLogExporter and OTLPSpanExporter,
ensuring that all required OTLP-related environment variables are set before initialization.

Usage:
    from otel.otlp import use_open_telemetry_otlp

    app = Application()
    use_open_telemetry_otlp(app)
"""

import os

from blacksheep import Application
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

from . import use_open_telemetry


__all__ = ["use_open_telemetry_otlp"]


def use_open_telemetry_otlp(app: Application):
    """
    Configures OpenTelemetry for a BlackSheep application using OTLP exporters.

    This function checks for required OTLP-related environment variables and sets up
    OpenTelemetry logging and tracing using OTLPLogExporter and OTLPSpanExporter.

    Args:
        app: The BlackSheep Application instance.

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
    )
