# Examples for OpenTelemetry integration

This folder contains examples to use [OpenTelemetry](https://opentelemetry.io/)
integration with [Grafana](https://grafana.com/), and with [Azure Application
Insights](https://learn.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview).

## Requirements

```bash
pip install opentelemetry-distro opentelemetry-exporter-otlp

opentelemetry-bootstrap --action=install
```

For *Azure Application Insights*, also install:

```bash
pip install azure-monitor-opentelemetry-exporter
```

To test, install also `blacksheep` and an ASGI server of your choice. For instance, `uvicorn`.

```bash
pip install blacksheep uvicorn
```

### Running the Azure example

1. Install the dependencies like documented above, including
   `azure-monitor-opentelemetry-exporter`.
2. Configure an environment variable `APP_INSIGHTS_CONNECTION_STRING` containing
   the connection string of an Azure Application Insights service.
3. Run the application with `uvicorn azureexample:app`.
4. Generate some web requests to the example endpoints `/`, `/bad-request`,
   `/crash`, `/example`.
5. Observe how logs appear in the Azure Application Insights service.

### Running the Grafana example

1. Install the dependencies like documented above, including
   `azure-monitor-opentelemetry-exporter`.
2. Obtain the necessary environment variables from the Grafana interface.
3. Configure the environment variables. These variables can also be configured
   in a `.env` file.
4. Run the application with `uvicorn grafanaexample:app`.
5. Generate some web requests to the example endpoints `/`, `/bad-request`,
   `/crash`, `/example`.
6. Observe how logs appear in the Azure Application Insights service.

Environment variables look like the following:

```
OTEL_RESOURCE_ATTRIBUTES="service.name=my-app,service.namespace=my-application-group,deployment.environment=production"
OTEL_EXPORTER_OTLP_ENDPOINT="https://otlp-gateway-prod-eu-north-0.grafana.net/otlp"
OTEL_EXPORTER_OTLP_HEADERS="Authorization=Basic%20******"
OTEL_EXPORTER_OTLP_PROTOCOL="http/protobuf"
```

## Folder structure

- The `otel` package contains reusable code.
- `otel.otlp` contains generic code that can be used with many services adhering to the OpenTelemetry standard, including Grafana.
