# Common Patterns

## Pattern 1: Sizing for Simple REST APIs

**When to Use:** Standard CRUD APIs, microservices, backend services with typical load.

### Starting Configuration

```yaml
# my-service.yml
service:
  type: ecs
  port: 8000

  resources:
    cpu: 512        # 0.5 vCPU
    memory: 1024    # 1 GB

  autoScaling:
    minCount: 2     # High availability
    maxCount: 10
    targetCPU: 70
```

### Expected Performance

**Throughput:**
- **Python (FastAPI):** 50-150 requests/second per task
- **Node.js (Express):** 100-300 requests/second per task
- **Go:** 500-2,000 requests/second per task

**Latency:**
- p50: 10-50ms
- p99: 50-200ms

### When to Scale Up

**Indicators you need more resources:**

```bash
# Check average CPU usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=my-service \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-07T23:59:59Z \
  --period 3600 \
  --statistics Average

# If average CPU > 70%: Scale up or scale out
```

**Decision matrix:**

| CPU Usage | Memory Usage | Action |
|-----------|--------------|--------|
| < 50% | < 50% | ✅ Current size is good |
| 50-70% | 50-70% | ⚠️  Monitor, prepare to scale |
| > 70% | < 60% | ⬆️ Scale CPU (1024) |
| < 60% | > 70% | ⬆️ Scale memory (2048) |
| > 70% | > 70% | ⬆️ Scale both (1024/2048) |

### Scaling Path

```yaml
# Phase 1: Start (low traffic)
resources:
  cpu: 512
  memory: 1024
autoScaling:
  minCount: 2
  maxCount: 10

# Phase 2: Growth (CPU bottleneck)
resources:
  cpu: 1024      # Doubled CPU
  memory: 1024   # Keep memory same
autoScaling:
  minCount: 2
  maxCount: 20   # Allow more scale-out

# Phase 3: High traffic (both bottlenecks)
resources:
  cpu: 1024
  memory: 2048   # Doubled memory
autoScaling:
  minCount: 5    # Higher baseline
  maxCount: 50
```

**Pitfalls:**
- Jumping from 512 to 4096 CPU without testing intermediate sizes
- Not correlating CPU spikes with actual request volume (may be a bug)
- Scaling resources when the problem is inefficient code (N+1 queries, missing indexes)

---

## Pattern 2: Sizing for Background Workers

**When to Use:** Celery workers, job processors, batch tasks, queue consumers.

### Starting Configuration

```yaml
# worker-service.yml
service:
  type: ecs
  port: 8000  # Health check only, no user traffic

  resources:
    cpu: 1024      # 1 vCPU (more compute)
    memory: 2048   # 2 GB (larger batches)

  autoScaling:
    minCount: 1    # Can start with 1 for workers
    maxCount: 20
    targetCPU: 80  # Workers can handle higher CPU
```

### Expected Performance

**Job throughput:**
- Light jobs (< 1 second): 100-500 jobs/minute per task
- Medium jobs (1-10 seconds): 10-50 jobs/minute per task
- Heavy jobs (> 10 seconds): 1-10 jobs/minute per task

### Monitoring Worker-Specific Metrics

```python
# Example: Custom CloudWatch metric for job queue depth
import boto3

cloudwatch = boto3.client('cloudwatch')

def report_queue_depth(queue_name, depth):
    cloudwatch.put_metric_data(
        Namespace='Workers',
        MetricData=[{
            'MetricName': 'QueueDepth',
            'Value': depth,
            'Unit': 'Count',
            'Dimensions': [{'Name': 'QueueName', 'Value': queue_name}]
        }]
    )

# Scale based on queue depth, not just CPU
```

### Auto-Scaling Based on Queue Depth

```yaml
# Custom auto-scaling target (not just CPU/memory)
autoScaling:
  minCount: 1
  maxCount: 50
  policies:
    - type: target-tracking
      metric: QueueDepth
      targetValue: 100    # Keep queue below 100 items
```

### When Workers Need More Resources

**Memory issues:**
```
Symptom: Tasks restarting with OutOfMemoryError
Cause: Processing large batches, loading large files
Solution: Increase memory to 4096 or 8192 MB
```

**CPU issues:**
```
Symptom: Job processing time increasing, queue backing up
Cause: CPU-bound tasks (data transformation, compression)
Solution: Increase CPU to 2048 or scale out (more tasks)
```

### Sizing Examples

| Job Type | CPU | Memory | Example |
|----------|-----|--------|---------|
| **Email sender** | 512 | 1024 | Simple API calls |
| **Image resizing** | 1024 | 2048 | CPU-bound, moderate memory |
| **Video transcoding** | 4096 | 8192 | Heavy CPU + memory |
| **Data ETL** | 2048 | 4096 | Database operations |
| **PDF generation** | 1024 | 4096 | Memory-bound (templates) |

**Pitfalls:**
- Setting minCount=0 (cold start delays when queue backs up)
- Not monitoring queue depth (CPU looks fine but queue is growing)
- Using same resources as API servers (workers need different sizing)

---

## Pattern 3: Sizing for ML Services

**When to Use:** Model inference, ML predictions, AI services.

### Starting Configuration

```yaml
# ml-service.yml
service:
  type: ecs
  port: 8000

  resources:
    cpu: 2048      # 2 vCPU (model inference)
    memory: 8192   # 8 GB (model loading)

  autoScaling:
    minCount: 2    # Keep models warm
    maxCount: 10
    targetCPU: 60  # Lower threshold for ML workloads
```

### Model Loading Considerations

```python
# Example: FastAPI ML service with model caching
from fastapi import FastAPI
import pickle
import os

app = FastAPI()

# Load model once on startup (not per request)
MODEL_PATH = "/app/models/model.pkl"
model = None

@app.on_event("startup")
def load_model():
    global model
    print(f"Loading model from {MODEL_PATH}...")
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    print(f"Model loaded, size: {os.path.getsize(MODEL_PATH) / 1024 / 1024:.2f} MB")

@app.post("/predict")
def predict(data: dict):
    prediction = model.predict([data['features']])
    return {"prediction": prediction.tolist()}
```

**Memory sizing rule:**
```
Memory needed = (Model size × 2) + (Request batch size × input size) + Overhead

Example:
- Model size: 2 GB
- Request batch: 100 items × 10 KB = 1 MB
- Python overhead: 200 MB
- Total: (2 GB × 2) + 1 MB + 200 MB = 4.2 GB
- Recommended: 8192 MB (2x buffer)
```

### Performance Benchmarking

```bash
# Test inference latency under load
hey -n 1000 -c 10 -m POST \
  -H "Content-Type: application/json" \
  -d '{"features": [1, 2, 3, 4, 5]}' \
  https://my-ml-service.com/predict

# Look for:
# - p99 latency < 500ms
# - No 503 errors (memory exhaustion)
# - CPU usage 50-70% (room to handle spikes)
```

### Sizing by Model Type

| Model Type | CPU | Memory | Notes |
|------------|-----|--------|-------|
| **Sklearn (< 100 MB)** | 1024 | 2048 | Lightweight models |
| **Sklearn (100 MB - 1 GB)** | 1024 | 4096 | Medium models |
| **TensorFlow/PyTorch (< 2 GB)** | 2048 | 8192 | Standard deep learning |
| **Large language model (> 5 GB)** | 4096 | 16384+ | Transformers, BERT |
| **Inference with GPU** | N/A | N/A | Use EC2 GPU instances, not Fargate |

### Optimization Strategies

**1. Model quantization (reduce memory):**
```python
# Convert float32 to int8 (4x memory reduction)
import tensorflow as tf

converter = tf.lite.TFLiteConverter.from_saved_model('model/')
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()
```

**2. Lazy loading (reduce startup time):**
```python
# Load model on first request, not startup
model = None

def get_model():
    global model
    if model is None:
        model = load_model_from_disk()
    return model
```

**3. Model caching (reduce redundant inference):**
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def predict_cached(features_tuple):
    return model.predict([list(features_tuple)])
```

**Pitfalls:**
- Not loading model on startup (cold start latency on first request)
- Using CPU-only for large models (too slow; use GPU instances)
- Not profiling memory usage (OOM kills during inference)

---

## Pattern 4: CloudWatch Dashboard Setup

**When to Use:** Monitoring new services, debugging performance issues.

### Creating a Dashboard

```bash
# Create CloudWatch dashboard with AWS CLI
aws cloudwatch put-dashboard \
  --dashboard-name my-service-metrics \
  --dashboard-body file://dashboard.json
```

```json
// dashboard.json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/ECS", "CPUUtilization", {"stat": "Average"}],
          [".", ".", {"stat": "Maximum"}]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "CPU Utilization",
        "yAxis": {"left": {"min": 0, "max": 100}}
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/ECS", "MemoryUtilization", {"stat": "Average"}],
          [".", ".", {"stat": "Maximum"}]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "Memory Utilization",
        "yAxis": {"left": {"min": 0, "max": 100}}
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/ApplicationELB", "TargetResponseTime", {"stat": "p99"}]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "p99 Latency"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/ApplicationELB", "RequestCount", {"stat": "Sum"}]
        ],
        "period": 300,
        "stat": "Sum",
        "region": "us-east-1",
        "title": "Request Count"
      }
    }
  ]
}
```

### Key Metrics to Monitor

| Metric | Namespace | Alarm Threshold | Why It Matters |
|--------|-----------|-----------------|----------------|
| **CPUUtilization** | AWS/ECS | > 70% for 5 min | Throttling increases latency |
| **MemoryUtilization** | AWS/ECS | > 80% for 5 min | OOM kills incoming |
| **TargetResponseTime** | AWS/ApplicationELB | p99 > 500ms | User experience degrading |
| **HealthyHostCount** | AWS/ApplicationELB | < minCount | Service availability issue |
| **UnHealthyHostCount** | AWS/ApplicationELB | > 0 for 5 min | Deployment or health check problem |

### Setting Up Alarms

```bash
# CPU alarm
aws cloudwatch put-metric-alarm \
  --alarm-name my-service-high-cpu \
  --alarm-description "Alert when CPU > 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:alerts

# Memory alarm
aws cloudwatch put-metric-alarm \
  --alarm-name my-service-high-memory \
  --alarm-description "Alert when Memory > 85%" \
  --metric-name MemoryUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 85 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:alerts
```

**Pitfalls:**
- Setting alarms without actionable thresholds (alert fatigue)
- Monitoring average CPU only (misses p99 spikes)
- Not tracking p99 latency (users experience worst-case, not average)

---

## Pattern 5: Interpreting CPU/Memory Metrics

**When to Use:** Diagnosing performance issues, deciding when to scale.

### Reading CloudWatch Graphs

#### Healthy Service Pattern

```
CPU Utilization:
Average: 40-60%
Maximum: 70-80%
Pattern: Stable, gradual fluctuations

Memory Utilization:
Average: 40-60%
Maximum: 70-75%
Pattern: Stable, slight upward trend during traffic

Interpretation: ✅ Service is healthy, room to handle traffic spikes
```

#### CPU Throttling Pattern

```
CPU Utilization:
Average: 85-95%
Maximum: 100%
Pattern: Sustained high usage, flat line at 100%

p99 Latency:
Baseline: 50ms
During high CPU: 500ms (10x increase)

Interpretation: ⚠️ CPU bottleneck, requests are being throttled
Action: Scale up CPU or scale out (more tasks)
```

#### Memory Exhaustion Pattern

```
Memory Utilization:
Average: 70-85%
Maximum: 95-100%
Pattern: Gradual increase over time (memory leak?)

Logs:
"OutOfMemoryError: Container killed due to memory usage"

Interpretation: ❌ Memory leak or insufficient memory
Action: Profile application for leaks, increase memory allocation
```

#### Traffic Spike Pattern

```
Request Count:
Baseline: 100 req/min
Spike: 1000 req/min (10x)

CPU Utilization:
Baseline: 30%
Spike: 90% (auto-scaling triggered)

Task Count:
Baseline: 2 tasks
Spike: 5 tasks (auto-scaled out)
After spike: 2 tasks (scaled in after 15 min)

Interpretation: ✅ Auto-scaling working correctly
```

### Common Anti-Patterns

#### Anti-Pattern 1: Ignoring p99 Latency

```
❌ Bad interpretation:
"Average latency is 50ms, service is fine"

Reality:
- p50 latency: 30ms
- p95 latency: 100ms
- p99 latency: 2000ms ⚠️  (99th percentile users wait 2 seconds!)

✅ Correct interpretation:
"p99 latency is 2 seconds, 1% of users have poor experience"
Action: Investigate slow queries, increase resources, or add caching
```

#### Anti-Pattern 2: Not Correlating Metrics

```
❌ Bad: Look at CPU in isolation
"CPU is at 90%, we need more CPU"

✅ Good: Correlate CPU with request volume
"CPU is at 90%, but request volume is normal (not a spike)"
This suggests inefficient code, not insufficient resources
Action: Profile code, optimize hot paths, THEN consider scaling
```

#### Anti-Pattern 3: Reacting to Short Spikes

```
❌ Bad: Scale up after 1-minute spike
"CPU hit 95% for 1 minute, let's double resources"

✅ Good: Look at sustained patterns
"CPU averages 50%, with occasional 2-minute spikes to 85%"
This is normal traffic variation, auto-scaling handles it
Action: No changes needed, auto-scaling is working
```

---

## Pattern 6: When to Scale Up vs Scale Out

**When to Use:** Deciding between vertical scaling (more CPU/memory per task) vs horizontal scaling (more tasks).

### Decision Matrix

| Scenario | Scale Up (Vertical) | Scale Out (Horizontal) |
|----------|---------------------|------------------------|
| **CPU bound** | ✅ Good | ✅ Good (preferred) |
| **Memory bound** | ✅ Good | ❌ Doesn't help (each task needs same memory) |
| **Latency bound** | ✅ Good (faster per-request processing) | ⚠️  May not help (more tasks, same latency) |
| **Throughput bound** | ⚠️  Limited gains | ✅ Good (linear scaling) |
| **State/session based** | ✅ Good (keeps state in one task) | ❌ Complicated (need sticky sessions) |
| **Stateless** | ⚠️  Works but inefficient | ✅ Ideal (distribute load) |
| **Cost optimization** | ⚠️  Hits Fargate size limits | ✅ Flexible (scale in during low traffic) |

### Scale Up (Vertical) Examples

#### Example 1: Memory-Bound ML Service

```yaml
# Before: OOM kills under load
resources:
  cpu: 2048
  memory: 4096    # Model + data doesn't fit
autoScaling:
  minCount: 2
  maxCount: 10

# After: Scaled up memory
resources:
  cpu: 2048       # Keep CPU same
  memory: 8192    # Doubled memory
autoScaling:
  minCount: 2     # Keep task count same
  maxCount: 10
```

**Why scale up:**
- Model loading requires 3 GB per task
- Scaling out doesn't help (each task needs 3 GB)
- Vertical scaling is only option

#### Example 2: Latency-Sensitive API

```yaml
# Before: p99 latency 500ms, CPU throttling
resources:
  cpu: 512        # Requests wait in queue
  memory: 1024

# After: Scaled up CPU
resources:
  cpu: 1024       # 2x CPU = 2x throughput per task
  memory: 1024    # Keep memory same
```

**Why scale up:**
- Requests are CPU-bound (complex calculations)
- More CPU per task = faster per-request processing
- Reduces latency spikes

### Scale Out (Horizontal) Examples

#### Example 1: High-Throughput API

```yaml
# Before: 2 tasks handling 200 req/sec total (100 req/sec each)
resources:
  cpu: 1024
  memory: 2048
autoScaling:
  minCount: 2
  maxCount: 10

# After: Auto-scaled to 5 tasks
# Now handling 500 req/sec total (100 req/sec each)
# Task count: 5 (automatically scaled)
```

**Why scale out:**
- Stateless API (any task can handle any request)
- Need more total throughput, not faster per-request
- Cost-efficient (scale in during low traffic)

#### Example 2: Background Job Processor

```yaml
# Before: Queue depth growing, 1 worker processing 10 jobs/min
resources:
  cpu: 1024
  memory: 2048
autoScaling:
  minCount: 1
  maxCount: 20
  policies:
    - metric: QueueDepth
      targetValue: 100

# After: Auto-scaled to 10 workers
# Now processing 100 jobs/min total
# Queue depth back to normal
```

**Why scale out:**
- Each job has similar resource requirements
- More workers = more parallel processing
- Linear scaling (10x workers = 10x throughput)

### When to Do Both

```yaml
# Phase 1: Baseline (low traffic)
resources:
  cpu: 512
  memory: 1024
autoScaling:
  minCount: 2
  maxCount: 10

# Phase 2: Scale up (memory bottleneck identified)
resources:
  cpu: 512
  memory: 2048    # Scaled up memory
autoScaling:
  minCount: 2
  maxCount: 10

# Phase 3: Scale out (traffic growth)
resources:
  cpu: 512
  memory: 2048
autoScaling:
  minCount: 5     # Higher baseline
  maxCount: 50    # Allow more scale-out

# Phase 4: Scale up again (CPU bottleneck)
resources:
  cpu: 1024       # Scaled up CPU
  memory: 2048
autoScaling:
  minCount: 5
  maxCount: 50
```

### Cost Comparison: Scale Up vs Scale Out

**Scenario: Need to handle 500 req/sec**

#### Option 1: Scale Up

```
Configuration: 2 tasks × 2048 CPU / 4096 MB
Cost: $84.50/month × 2 = $169/month
Throughput: 500 req/sec (250 req/sec per task)
```

#### Option 2: Scale Out

```
Configuration: 5 tasks × 512 CPU / 1024 MB
Cost: $17.91/month × 5 = $89.55/month
Throughput: 500 req/sec (100 req/sec per task)
Savings: 47% ($79.45/month)
```

**Scale out is cheaper for throughput-bound workloads.**

**Pitfalls:**
- Scaling up when scaling out would be cheaper
- Scaling out for memory-bound workloads (doesn't help)
- Not testing both approaches (scale up might be faster for your use case)

---

## Summary

**Key patterns:**
1. **Simple REST APIs** - Start 512/1024, scale to 1024/2048
2. **Background workers** - Start 1024/2048, scale to 4096/8192
3. **ML services** - Start 2048/8192, optimize model loading
4. **CloudWatch dashboards** - Monitor CPU, memory, latency, request count
5. **Interpreting metrics** - Watch p99, correlate metrics, avoid short-term reactions
6. **Scale up vs out** - Scale out for throughput, scale up for memory/latency

**Next steps:**
- See `deploying-your-first-service` for initial deployment
- See `troubleshooting-ecs-deployments` for debugging resource issues
- See `fsd-yaml-config` for auto-scaling configuration
