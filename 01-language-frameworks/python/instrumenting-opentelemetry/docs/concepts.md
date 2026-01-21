# Core Concepts: OpenTelemetry Instrumentation

## What

OpenTelemetry is a vendor-neutral observability framework that provides distributed tracing, metrics, and logs. It instruments your Python services to automatically capture request flows across microservices, measure performance, and export telemetry data to backends like Grafana Tempo.

The Python SDK provides:
- **Auto-instrumentation** for popular libraries (FastAPI, httpx, aiokafka, boto3)
- **OTLP exporters** for gRPC and HTTP protocols
- **Context propagation** to track requests across service boundaries
- **Custom instrumentation** for business logic and domain-specific operations

## Why

**Problem: No Visibility into Distributed Systems**

In microservice architectures, a single user request can span dozens of services. Without tracing:
- Debugging production issues requires sifting through logs from multiple services
- Performance bottlenecks are hard to identify (is it the database? the API? network latency?)
- No way to track requests end-to-end or understand service dependencies
- Mean time to resolution (MTTR) increases as system complexity grows

**Solution: Automatic Distributed Tracing**

OpenTelemetry solves this by:
- Automatically creating spans for each operation (HTTP requests, database queries, message publishes)
- Propagating trace context via headers (W3C Trace Context standard)
- Exporting spans to centralized backends for visualization and analysis
- Enriching traces with custom attributes for business context

**Fetch Context**

At Fetch, services export traces via OTLP gRPC to OpenTelemetry collectors, which forward to Grafana Tempo. Developers use Grafana to:
- Query traces by service, endpoint, or trace ID
- Visualize request flows across the microservice graph
- Identify slow spans and performance regressions
- Correlate traces with logs using trace IDs

## How

**OTLP gRPC Export**

OpenTelemetry Protocol (OTLP) is the standard for exporting telemetry. The gRPC exporter:
- Sends spans to collectors on port 4317 (default)
- Uses Protobuf for efficient serialization
- Batches spans asynchronously to avoid blocking request handlers
- Supports TLS and compression for production environments

**Auto-Instrumentation**

Instrumentors wrap library code to create spans automatically:
```python
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

FastAPIInstrumentor().instrument()  # Wraps FastAPI handlers
HTTPXClientInstrumentor().instrument()  # Wraps httpx.Client calls
```

**Custom Spans**

For business logic not covered by auto-instrumentation:
```python
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("process_payment") as span:
    span.set_attribute("user.id", user_id)
    span.set_attribute("amount", amount)
    # Business logic here
```

**Trace IDs in Logs**

Link logs to traces for unified debugging:
```python
from opentelemetry import trace

span = trace.get_current_span()
trace_id = span.get_span_context().trace_id
logger.info(f"Processing request", extra={"trace_id": trace_id})
```

## When to Use

**Use when:**
- Building microservices that communicate via HTTP, gRPC, or messaging
- Debugging latency issues or identifying performance bottlenecks
- Implementing SLOs and need to track request success rates and durations
- Adopting observability best practices for production services
- Integrating with Fetch's Grafana/Tempo observability stack

**Avoid when:**
- Building scripts or CLIs that don't make external calls
- Performance overhead is unacceptable (though sampling mitigates this)
- No centralized backend to receive traces (local-only development)

## Key Terminology

- **Span** - A single operation in a trace (e.g., HTTP request, database query). Contains start time, duration, and attributes.
- **Trace** - A collection of spans representing a single request's journey through the system. Identified by a trace ID.
- **Tracer** - Factory for creating spans. Typically one per module or library.
- **Resource** - Metadata about the service (name, version, environment) attached to all telemetry.
- **OTLP** - OpenTelemetry Protocol for exporting telemetry. Supports gRPC and HTTP transports.
- **Collector** - Agent that receives, processes, and forwards telemetry to backends (e.g., Tempo, Jaeger).
- **Context Propagation** - Mechanism to pass trace context between services via HTTP headers or message metadata.
- **Instrumentation** - Code that creates spans and captures telemetry. Can be automatic (via libraries) or manual (via API).
