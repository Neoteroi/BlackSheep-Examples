"""
This module provides functions to configure OpenTelemetry logging with an
Azure Application Insights service.

To use, install the following dependencies:

Install:
    pip install opentelemetry-distro opentelemetry-exporter-otlp
    opentelemetry-bootstrap --action=install

    pip install azure-monitor-opentelemetry-exporter

Usage:
    from otel.azure import use_application_insights

    app = Application()
    use_application_insights(app, connection_string)
"""

from functools import wraps

from azure.monitor.opentelemetry.exporter import (
    AzureMonitorLogExporter,
    AzureMonitorTraceExporter,
)
from blacksheep import Application

from . import client_span_context, use_open_telemetry


__all__ = ["use_application_insights", "log_dependency"]


def use_application_insights(
    app: Application,
    connection_string: str,
):
    """
    Configures OpenTelemetry for a BlackSheep application using Azure Application Insights.

    Sets up logging and tracing exporters for Azure Monitor using the provided connection string.

    Args:
        app: The BlackSheep Application instance.
        connection_string: Azure Application Insights connection string.
    """
    use_open_telemetry(
        app,
        AzureMonitorLogExporter(connection_string=connection_string),
        AzureMonitorTraceExporter(connection_string=connection_string),
    )


def log_dependency(namespace="Service"):
    """
    Wraps a function to log each call using OpenTelemetry, as dependency
    in Azure Application Insights.
    """

    def log_decorator(fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            with client_span_context(
                fn.__name__, {"az.namespace": namespace}, *args, **kwargs
            ):
                return await fn(*args, **kwargs)

        return wrapper

    return log_decorator
