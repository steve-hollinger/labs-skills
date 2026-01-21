# Code Patterns: OpenTelemetry Instrumentation

## Pattern 1: Basic OTLP Configuration

**When to Use:** Setting up OpenTelemetry for any Python service that needs to export traces and metrics to Fetch's observability stack (Grafana/Tempo).

```python
# src/observability.py
import logging
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

logger = logging.getLogger(__name__)


def setup_observability(
    service_name: str,
    service_version: str,
    environment: str,
    otlp_endpoint: str = "http://otel-collector:4317"
):
    """Configure OpenTelemetry with OTLP gRPC exporters.

    Args:
        service_name: Service identifier (e.g., "user-service")
        service_version: Deployment version (e.g., "1.2.3")
        environment: Environment name (e.g., "prod", "stage")
        otlp_endpoint: OTLP gRPC collector endpoint (port 4317)
    """
    # Create resource with service metadata for Tempo filtering
    resource = Resource(attributes={
        "service.name": service_name,
        "service.version": service_version,
        "deployment.environment": environment,
    })

    # Setup distributed tracing
    trace_exporter = OTLPSpanExporter(
        endpoint=otlp_endpoint,
        insecure=True  # Use TLS in production with port 4318
    )
    trace_provider = TracerProvider(resource=resource)
    trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
    trace.set_tracer_provider(trace_provider)

    # Setup metrics
    metric_exporter = OTLPMetricExporter(
        endpoint=otlp_endpoint,
        insecure=True
    )
    metric_reader = PeriodicExportingMetricReader(
        metric_exporter,
        export_interval_millis=60000  # Export every 60s
    )
    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[metric_reader]
    )
    metrics.set_meter_provider(meter_provider)

    logger.info(
        f"OpenTelemetry configured: service={service_name} "
        f"endpoint={otlp_endpoint}"
    )


# main.py
from src.observability import setup_observability
from src.config import settings

# MUST call before importing FastAPI or other instrumented libraries
setup_observability(
    service_name=settings.service_name,
    service_version=settings.version,
    environment=settings.environment,
    otlp_endpoint=settings.otel_endpoint
)

from fastapi import FastAPI  # Import after setup
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

app = FastAPI()
FastAPIInstrumentor.instrument_app(app)  # Auto-instrument all routes
```

**Pitfalls:**
- **Wrong port number**: OTLP gRPC uses 4317, not 4318 (HTTP). Using HTTP port with gRPC exporter fails silently.
- **Late initialization**: Setup must happen before FastAPI import. Auto-instrumentation wraps code at import time.
- **Missing resource attributes**: Without `service.name` and `deployment.environment`, traces are hard to filter in Grafana.

---

## Pattern 2: Custom Spans and Attributes

**When to Use:** Adding observability to business logic, database operations, or third-party libraries that don't have auto-instrumentation.

```python
# src/services/payment_service.py
import logging
from typing import Optional
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class PaymentService:
    async def process_payment(
        self,
        user_id: str,
        amount: float,
        payment_method: str
    ) -> dict:
        """Process payment with custom instrumentation."""

        # Create custom span for business operation
        with tracer.start_as_current_span("process_payment") as span:
            # Add custom attributes for filtering in Grafana
            span.set_attribute("user.id", user_id)
            span.set_attribute("payment.amount", amount)
            span.set_attribute("payment.method", payment_method)

            try:
                # Nested span for external API call
                with tracer.start_as_current_span("validate_payment_method") as validate_span:
                    validate_span.set_attribute("http.url", "https://payment-api.fetch.com/validate")
                    is_valid = await self._validate_payment_method(payment_method)
                    validate_span.set_attribute("validation.result", is_valid)

                    if not is_valid:
                        raise ValueError(f"Invalid payment method: {payment_method}")

                # Nested span for database write
                with tracer.start_as_current_span("record_transaction") as db_span:
                    db_span.set_attribute("db.system", "postgresql")
                    db_span.set_attribute("db.operation", "INSERT")
                    transaction_id = await self._record_transaction(user_id, amount)
                    db_span.set_attribute("transaction.id", transaction_id)

                # Mark span as successful
                span.set_status(Status(StatusCode.OK))
                span.set_attribute("payment.status", "success")

                return {"transaction_id": transaction_id, "status": "success"}

            except Exception as e:
                # Record exception as span event
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.set_attribute("payment.status", "failed")

                # Get trace ID for log correlation
                trace_id = format(span.get_span_context().trace_id, "032x")
                logger.error(
                    f"Payment processing failed: {e}",
                    extra={"trace_id": trace_id, "user_id": user_id}
                )
                raise


    async def _validate_payment_method(self, payment_method: str) -> bool:
        # Implementation
        return True

    async def _record_transaction(self, user_id: str, amount: float) -> str:
        # Implementation
        return "txn_123456"


# src/utils/logging.py
from opentelemetry import trace
import logging


def get_trace_id() -> Optional[str]:
    """Extract trace ID from current span context for log correlation."""
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        # Format as 32-character hex string matching Tempo format
        return format(span.get_span_context().trace_id, "032x")
    return None


class TraceIdFilter(logging.Filter):
    """Inject trace ID into all log records."""

    def filter(self, record):
        record.trace_id = get_trace_id() or "no-trace"
        return True


# Configure logging with trace IDs
handler = logging.StreamHandler()
handler.addFilter(TraceIdFilter())
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s [%(trace_id)s] %(name)s: %(message)s'
)
handler.setFormatter(formatter)
logging.root.addHandler(handler)
```

**Pitfalls:**
- **Forgetting to set status**: Always call `span.set_status()` on success and failure. Unset status defaults to "unset" which looks like an error in Grafana.
- **Too many attributes**: Limit to 10-15 attributes per span. Excessive attributes increase payload size and slow down Tempo queries.
- **Blocking operations in span**: Keep span scope tight around the operation being measured. Don't include long waits or unrelated code.

---

## Pattern 3: Auto-Instrumentation for FastAPI, aiokafka, and boto3

**When to Use:** Automatically instrument common libraries used at Fetch without manual span creation. Provides zero-code observability for HTTP, messaging, and AWS calls.

```python
# src/observability.py
import logging
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.aiokafka import AioKafkaInstrumentor
from opentelemetry.instrumentation.boto3sqs import Boto3SQSInstrumentor
from opentelemetry.instrumentation.botocore import BotocoreInstrumentor

logger = logging.getLogger(__name__)


def instrument_libraries():
    """Auto-instrument all common libraries used in Fetch services."""

    # FastAPI: Instruments all routes, creates spans for each request
    # Captures: HTTP method, path, status code, duration
    FastAPIInstrumentor().instrument()

    # HTTPX: Instruments outbound HTTP calls
    # Captures: request URL, method, response status, headers
    HTTPXClientInstrumentor().instrument()

    # aiokafka: Instruments Kafka producers and consumers
    # Captures: topic, partition, offset, message size
    AioKafkaInstrumentor().instrument()

    # boto3 SQS: Instruments SQS send/receive operations
    # Captures: queue URL, message ID, message attributes
    Boto3SQSInstrumentor().instrument()

    # botocore: Instruments all AWS SDK calls (S3, DynamoDB, etc.)
    # Captures: service name, operation, region
    BotocoreInstrumentor().instrument()

    logger.info("Auto-instrumentation enabled for all libraries")


# main.py
from src.observability import setup_observability, instrument_libraries
from src.config import settings

# Step 1: Configure OTLP exporters
setup_observability(
    service_name=settings.service_name,
    service_version=settings.version,
    environment=settings.environment
)

# Step 2: Enable auto-instrumentation BEFORE importing libraries
instrument_libraries()

# Step 3: Import and use libraries normally
from fastapi import FastAPI
import httpx
import boto3
from aiokafka import AIOKafkaProducer

app = FastAPI()


@app.get("/users/{user_id}")
async def get_user(user_id: str):
    """Auto-instrumented: Creates span automatically."""

    # HTTP call to another service: auto-instrumented by HTTPX
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.fetch.com/users/{user_id}")
        user_data = response.json()

    # AWS call: auto-instrumented by botocore
    s3 = boto3.client("s3")
    s3.get_object(Bucket="user-avatars", Key=f"{user_id}.jpg")

    return user_data


# src/kafka/producer.py
from aiokafka import AIOKafkaProducer
from opentelemetry import trace


class EventProducer:
    def __init__(self, bootstrap_servers: str):
        # AIOKafkaProducer is auto-instrumented
        self.producer = AIOKafkaProducer(bootstrap_servers=bootstrap_servers)

    async def send_event(self, topic: str, event: dict):
        """Send event to Kafka. Automatically creates span and propagates trace context."""
        # Trace context is automatically injected into Kafka message headers
        await self.producer.send_and_wait(topic, value=event.encode())


# src/kafka/consumer.py
from aiokafka import AIOKafkaConsumer
from opentelemetry import trace


class EventConsumer:
    def __init__(self, bootstrap_servers: str, topic: str):
        # AIOKafkaConsumer is auto-instrumented
        self.consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            group_id="my-group"
        )

    async def process_events(self):
        """Process events from Kafka. Trace context is automatically extracted."""
        async for message in self.consumer:
            # Trace context from producer is automatically extracted from headers
            # New span is created as child of producer's span

            # Get trace ID for logging
            span = trace.get_current_span()
            trace_id = format(span.get_span_context().trace_id, "032x")

            print(f"Processing message [trace_id={trace_id}]: {message.value}")
            # Business logic here...


# pyproject.toml dependencies
# [tool.poetry.dependencies]
# opentelemetry-api = "^1.20.0"
# opentelemetry-sdk = "^1.20.0"
# opentelemetry-exporter-otlp-proto-grpc = "^1.20.0"
# opentelemetry-instrumentation-fastapi = "^0.41b0"
# opentelemetry-instrumentation-httpx = "^0.41b0"
# opentelemetry-instrumentation-aiokafka = "^0.41b0"
# opentelemetry-instrumentation-boto3sqs = "^0.41b0"
# opentelemetry-instrumentation-botocore = "^0.41b0"
```

**Pitfalls:**
- **Instrumenting after imports**: Call `instrument()` before importing FastAPI/httpx/etc. Instrumentation wraps code at import time, so late calls won't work.
- **Missing trace context in Kafka**: Ensure producer and consumer use compatible OpenTelemetry versions. Mismatched versions break context propagation.
- **Performance overhead**: Auto-instrumentation adds 1-5ms latency per operation. Use sampling (e.g., 10% of traces) for high-throughput services to reduce overhead.
- **Duplicate instrumentation**: Calling `instrument()` multiple times on the same library can cause double-wrapped spans. Only call once per library.

---

## Additional Patterns

### Context Propagation in Background Tasks

When spawning async tasks, trace context doesn't automatically propagate:

```python
import asyncio
from opentelemetry import trace, context

async def background_task(task_id: str):
    # Will NOT have trace context by default
    span = trace.get_current_span()
    print(f"Trace ID: {span.get_span_context().trace_id}")  # Shows invalid

# Correct way: Capture and attach context
async def handle_request():
    with tracer.start_as_current_span("main_request"):
        # Capture current context
        ctx = context.get_current()

        # Attach context in background task
        asyncio.create_task(
            context.attach(ctx),
            background_task("task-123")
        )
```

### Sampling Configuration

Reduce overhead in high-throughput services:

```python
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

# Sample 10% of traces
sampler = TraceIdRatioBased(rate=0.1)
trace_provider = TracerProvider(resource=resource, sampler=sampler)
```