# Core Concepts

## What is a vCPU?

**vCPU (virtual CPU)** = A single hyperthread of a physical CPU core.

**In practical terms:**
- **1024 vCPU units** = 1 full vCPU = 1 hyperthread
- **512 vCPU units** = 0.5 vCPU = Half a hyperthread
- **2048 vCPU units** = 2 vCPUs = 2 hyperthreads

**What does this mean for your application?**

```
512 CPU (0.5 vCPU):
- Can handle ~50-100 requests/second for simple APIs
- Good for lightweight web services
- Will throttle under sustained high load

1024 CPU (1 vCPU):
- Can handle ~100-500 requests/second for typical APIs
- Good for most backend services
- Suitable for moderate compute workloads

2048 CPU (2 vCPU):
- Can handle ~500-2,000 requests/second
- Good for CPU-intensive tasks (image processing, ML inference)
- Suitable for background job processors
```

**CPU throttling vs CPU limit:**
- **CPU limit** - Maximum CPU your container can use
- **CPU throttling** - When demand exceeds limit, processes slow down (don't crash)
- **Effect on users** - Increased latency (p95/p99 latency spikes)

**Example:**
```
Service with 512 CPU (0.5 vCPU):
- Normal load: 40% CPU usage, p99 latency = 50ms ✅
- High load: 100% CPU usage, p99 latency = 500ms ⚠️  (throttled)
- Solution: Scale to 1024 CPU or scale out (more tasks)
```

## Memory Limits and OOM Kills

**Memory is hard-limited** - Unlike CPU (which throttles), exceeding memory limit kills the container.

**What happens when memory is exhausted:**
```
Container memory usage: 950 MB / 1024 MB (93%) ✅ OK
Container memory usage: 1024 MB / 1024 MB (100%) ⚠️  Warning
Container memory usage: 1025 MB / 1024 MB ❌ OOM Kill (process terminated)
```

**ECS behavior on OOM:**
1. Container process is killed immediately
2. ECS restarts the task
3. Health checks fail during restart
4. ALB stops routing traffic to the task
5. If persistent, task enters restart loop

**CloudWatch Logs show:**
```
Essential container in task exited
Task stopped reason: OutOfMemoryError: Container killed due to memory usage
```

**How to prevent OOM kills:**
- Monitor memory usage in CloudWatch (stay below 80%)
- Profile application memory leaks (heap dumps, memory profilers)
- Set memory limit 20-30% higher than peak usage
- For Python: Consider using memory-efficient libraries (generators vs lists)
- For Node.js: Tune `--max-old-space-size` flag

**Memory usage patterns:**
```
Python (FastAPI):
- Baseline: 100-200 MB
- Per request: +5-20 MB (garbage collected)
- Peak: 300-500 MB (under load)
- Recommended: 1024 MB (2x peak)

Node.js (Express):
- Baseline: 50-100 MB
- Per request: +2-10 MB
- Peak: 200-400 MB (under load)
- Recommended: 1024 MB (2.5x peak)

Go:
- Baseline: 10-50 MB
- Per request: +1-5 MB
- Peak: 100-200 MB (under load)
- Recommended: 512 MB (2.5x peak)
```

## Fargate CPU/Memory Combinations Table

**Fargate enforces valid CPU/memory combinations.** Not all combinations are allowed.

### Valid Combinations

| CPU (vCPU units) | Memory (MB) Options |
|------------------|---------------------|
| **256** (0.25 vCPU) | 512, 1024, 2048 |
| **512** (0.5 vCPU) | 1024, 2048, 3072, 4096 |
| **1024** (1 vCPU) | 2048, 3072, 4096, 5120, 6144, 7168, 8192 |
| **2048** (2 vCPU) | 4096, 5120, 6144, 7168, 8192, 9216, 10240, 11264, 12288, 13312, 14336, 15360, 16384 |
| **4096** (4 vCPU) | 8192 to 30720 (in 1024 MB increments) |
| **8192** (8 vCPU) | 16384 to 61440 (in 4096 MB increments) |
| **16384** (16 vCPU) | 32768 to 122880 (in 8192 MB increments) |

### Common Configurations

| Use Case | CPU | Memory | Notes |
|----------|-----|--------|-------|
| **Minimal API** | 256 | 512 | Very lightweight, limited throughput |
| **Simple API** | 512 | 1024 | Good starting point for most services |
| **Standard API** | 1024 | 2048 | Default for production services |
| **Worker/Job processor** | 1024 | 4096 | More memory for batch processing |
| **ML inference** | 2048 | 8192 | CPU + memory for model loading |
| **Heavy compute** | 4096 | 16384 | Image/video processing, data pipelines |

### Invalid Combinations (Will Fail Deployment)

❌ 512 CPU + 512 MB - Too little memory for 512 CPU
❌ 512 CPU + 8192 MB - Too much memory for 512 CPU
❌ 1024 CPU + 1024 MB - Too little memory for 1024 CPU
❌ 2048 CPU + 2048 MB - Too little memory for 2048 CPU

**Error message:**
```
Invalid resource requirements: Memory should be at least 2048MB for cpu value 1024
```

## Auto-Scaling Strategies

**Auto-scaling automatically adjusts the number of running tasks** based on CloudWatch metrics.

### ECS Auto-Scaling Configuration

```yaml
# FSD YAML
service:
  autoScaling:
    minCount: 2        # Minimum tasks (high availability)
    maxCount: 10       # Maximum tasks (cost limit)
    targetCPU: 70      # Scale when CPU > 70%
    targetMemory: 80   # Scale when Memory > 80%
```

### How Auto-Scaling Works

```
Current state: 2 tasks, each at 50% CPU
Load increases: CPU rises to 75% (above targetCPU of 70%)
Auto-scaling triggers: ECS launches 1 additional task
New state: 3 tasks, each at 50% CPU
Result: p99 latency returns to normal
```

### Scaling Policies

#### 1. Target Tracking (Recommended)

**When to use:** Most services (simple, automatic).

```yaml
autoScaling:
  minCount: 2
  maxCount: 10
  targetCPU: 70      # Maintain CPU at 70%
```

**How it works:**
- ECS monitors average CPU across all tasks
- If CPU > 70% for 3 minutes: Scale out (add tasks)
- If CPU < 70% for 15 minutes: Scale in (remove tasks)

**Benefits:**
- Simple to configure
- Predictable behavior
- Gradual scaling (prevents over-provisioning)

#### 2. Step Scaling

**When to use:** Need aggressive scaling for traffic spikes.

```yaml
autoScaling:
  minCount: 2
  maxCount: 20
  policies:
    - type: step
      metric: CPUUtilization
      steps:
        - lower: 0
          upper: 50
          adjustment: -1    # Remove 1 task if CPU < 50%
        - lower: 70
          upper: 85
          adjustment: +2    # Add 2 tasks if 70% < CPU < 85%
        - lower: 85
          upper: null
          adjustment: +5    # Add 5 tasks if CPU > 85%
```

**Benefits:**
- Fast response to traffic spikes
- More granular control
- Can scale by percentage (e.g., +50% capacity)

#### 3. Scheduled Scaling

**When to use:** Predictable traffic patterns (e.g., business hours).

```yaml
autoScaling:
  minCount: 2
  maxCount: 10
  schedules:
    - name: scale-up-morning
      cron: "0 8 * * MON-FRI"   # 8 AM weekdays
      minCount: 5
      maxCount: 20
    - name: scale-down-evening
      cron: "0 18 * * MON-FRI"  # 6 PM weekdays
      minCount: 2
      maxCount: 10
```

**Benefits:**
- Pre-scale before traffic arrives
- Reduce costs during off-hours
- Works for known patterns (daily, weekly)

### Choosing the Right Strategy

| Traffic Pattern | Strategy | Example |
|----------------|----------|---------|
| **Unpredictable** | Target Tracking | New service, variable load |
| **Spiky (sudden bursts)** | Step Scaling | Flash sales, viral content |
| **Predictable (daily)** | Scheduled + Target | Business hours traffic |
| **Steady** | Target Tracking (wide range) | Background jobs |

## Cost Comparison

**Fargate pricing** is based on vCPU-hour and GB-hour (us-east-1, 2024 pricing):
- **vCPU:** $0.04048 per vCPU per hour
- **Memory:** $0.004445 per GB per hour

### Monthly Cost Examples

| Configuration | vCPU Cost | Memory Cost | Total Monthly* | Use Case |
|---------------|-----------|-------------|----------------|----------|
| 256 CPU / 512 MB | $7.35 | $1.61 | **$8.96** | Minimal API |
| 512 CPU / 1024 MB | $14.69 | $3.22 | **$17.91** | Simple API |
| 1024 CPU / 2048 MB | $29.38 | $6.43 | **$35.81** | Standard API |
| 1024 CPU / 4096 MB | $29.38 | $12.87 | **$42.25** | Worker |
| 2048 CPU / 8192 MB | $58.76 | $25.74 | **$84.50** | ML service |
| 4096 CPU / 16384 MB | $117.51 | $51.47 | **$168.98** | Heavy compute |

*Assumes 1 task running 24/7 (730 hours/month)

### Cost Optimization Tips

#### 1. Right-Size Your Resources

```
Wasteful configuration:
- CPU allocation: 2048 (2 vCPU)
- Actual CPU usage: 10% average
- Wasted CPU: 90%
- Monthly cost: $58.76 for CPU alone

Optimized configuration:
- CPU allocation: 512 (0.5 vCPU)
- Actual CPU usage: 40% average
- Wasted CPU: 60% (acceptable)
- Monthly cost: $14.69 for CPU
- Savings: 75% ($44.07/month)
```

#### 2. Scale In During Off-Hours

```
Always-on (24/7):
- 5 tasks × 1024 CPU / 2048 MB
- Monthly cost: $179.05 × 5 = $895.25

Smart scaling (business hours only):
- Business hours (12 hrs/day, 5 days/week): 5 tasks
- Off-hours: 2 tasks
- Effective: ~3.2 tasks average
- Monthly cost: ~$573.76
- Savings: 36% ($321.49/month)
```

#### 3. Use Spot for Non-Critical Workloads

**Fargate Spot** = 70% cheaper, but tasks can be interrupted.

```
On-Demand:
- 1024 CPU / 2048 MB
- Monthly cost: $35.81

Fargate Spot:
- 1024 CPU / 2048 MB
- Monthly cost: $10.74
- Savings: 70% ($25.07/month)
```

**Use Spot for:**
- Background jobs (can retry)
- Batch processing
- Development/staging environments

**Don't use Spot for:**
- User-facing APIs (interruptions = downtime)
- Stateful services
- Services without retry logic

#### 4. Monitor and Adjust Regularly

**Set up monthly review:**
1. Check CloudWatch metrics (average CPU/memory usage)
2. If CPU/memory < 50% for 30 days: Scale down
3. If CPU/memory > 80% for 30 days: Scale up
4. Adjust auto-scaling thresholds based on traffic patterns

**Example review:**
```
Month 1:
- Allocated: 1024 CPU / 2048 MB
- Average usage: 20% CPU, 30% memory
- Action: Scale down to 512 CPU / 1024 MB
- Savings: 50%

Month 2:
- Allocated: 512 CPU / 1024 MB
- Average usage: 60% CPU, 50% memory
- Action: Keep current size (good utilization)
```

## Summary

**Key concepts:**
- **vCPU** - Virtual CPU hyperthread; 1024 units = 1 vCPU
- **Memory limits** - Hard limit; exceeding causes OOM kill
- **Fargate constraints** - Not all CPU/memory combinations are valid
- **Auto-scaling** - Automatically adjusts task count based on metrics
- **Cost** - Scales linearly with CPU and memory allocation

**Best practices:**
- Start small (512 CPU / 1024 MB)
- Monitor CloudWatch metrics (CPU, memory, latency)
- Scale gradually based on actual usage
- Use auto-scaling for variable traffic
- Review costs monthly and right-size

**Next:** See [patterns.md](patterns.md) for sizing examples and monitoring setup.
