---
name: instrumenting-opentelemetry
description: Add distributed tracing and metrics with OpenTelemetry for Python services. Use when implementing observability in FastAPI or async services.
tags: ['python', 'opentelemetry', 'tracing', 'metrics', 'observability', 'otlp']
---

# OpenTelemetry Instrumentation

## Quick Start
```python
# src/observability.py
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

def setup_observability(service_name: str, otlp_endpoint: str):
    # Create resource with service metadata
    resource = Resource(attributes={
        "service.name": service_name,
        "deployment.environment": "prod",
    })

    # Configure OTLP trace exporter via gRPC
    trace_exporter = OTLPSpanExporter(
        endpoint=otlp_endpoint,  # e.g., "http://otel-collector:4317"
        insecure=True
    )
    trace_provider = TracerProvider(resource=resource)
    trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
    trace.set_tracer_provider(trace_provider)

    # Configure OTLP metric exporter
    metric_exporter = OTLPMetricExporter(endpoint=otlp_endpoint, insecure=True)
    metric_reader = PeriodicExportingMetricReader(metric_exporter)
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)
```

## Key Points
- Use OTLP gRPC exporters for traces and metrics to integrate with Fetch's Grafana/Tempo stack
- Auto-instrument FastAPI, httpx, aiokafka, and boto3 for automatic span creation without code changes
- Add custom spans with `tracer.start_as_current_span()` for business logic and non-instrumented libraries
- Include trace IDs in logs using OpenTelemetry context for end-to-end request correlation
- Configure service resources (name, version, environment) for accurate service identification in Tempo

## Common Mistakes
1. **Forgetting to call setup before app initialization** - Setup observability before creating FastAPI app to ensure all handlers are instrumented. Auto-instrumentation only works on code loaded after setup.
2. **Using HTTP endpoint for gRPC exporters** - OTLP gRPC uses port 4317, not 4318 (HTTP). Wrong endpoint causes silent failures with no spans exported.
3. **Not propagating context in async tasks** - Use `attach()` and `detach()` when spawning background tasks or the trace context won't carry over, breaking distributed traces.
4. **Missing resource attributes** - Always set `service.name`, `service.version`, and `deployment.environment`. Without these, traces are hard to filter in Grafana.
5. **Blocking on span export** - Use `BatchSpanProcessor` (async batching) instead of `SimpleSpanProcessor` (synchronous) to avoid slowing down request handlers.

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples
