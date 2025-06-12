from blacksheep import Application
from . import use_open_telemetry


from azure.monitor.opentelemetry.exporter import (
    AzureMonitorLogExporter,
    AzureMonitorTraceExporter,
)


def use_application_insights(
    app: Application,
    connection_string: str,
    service_name: str = "unknown",
    service_namespace: str = "default",
    env: str = "",
):
    """
    Configures OpenTelemetry for a BlackSheep application using Azure Application Insights.

    Sets up logging and tracing exporters for Azure Monitor using the provided connection string.

    Args:
        app: The BlackSheep Application instance.
        connection_string: Azure Application Insights connection string.
        service_name: The name of the service (default: "unknown").
        service_namespace: The namespace of the service (default: "default").
        env: The deployment environment (default: "").
    """
    use_open_telemetry(
        app,
        AzureMonitorLogExporter(connection_string=connection_string),
        AzureMonitorTraceExporter(connection_string=connection_string),
        service_name,
        service_namespace,
        env,
    )
