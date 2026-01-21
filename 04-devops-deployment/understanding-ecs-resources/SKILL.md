---
name: understanding-ecs-resources
description: Right-size ECS/Fargate CPU and memory resources to balance performance and cost. Use when configuring resources for new services or troubleshooting performance issues.
tags: ['ecs', 'fargate', 'resources', 'performance', 'cost-optimization', 'aws']
---

# Understanding ECS Resources

## Quick Start

**Recommended starting configurations by service type:**

```yaml
# Simple REST API (e.g., FastAPI, Express)
resources:
  cpu: 512       # 0.5 vCPU
  memory: 1024   # 1 GB

# Background worker (e.g., Celery, job processor)
resources:
  cpu: 1024      # 1 vCPU
  memory: 2048   # 2 GB

# ML/AI service (e.g., model inference)
resources:
  cpu: 2048      # 2 vCPU
  memory: 4096   # 4 GB
```

**Valid Fargate CPU/Memory combinations:** Not all combinations work! Use the reference table in [concepts.md](docs/concepts.md).

## Key Points

- **Fargate has valid CPU/memory combinations** - Not all values work (e.g., 512 CPU + 4096 memory is invalid)
- **Start small, scale based on metrics** - Begin with 512 CPU / 1024 memory, monitor CloudWatch, then scale up if needed
- **CPU throttling hurts latency, memory exhaustion kills containers** - Watch both metrics; CPU impacts p99 latency, memory causes OOM kills
- **Auto-scaling responds to CPU/memory usage thresholds** - Set targetCPU to 70% for gradual scaling before performance degrades
- **Cost scales linearly with resources** - Doubling CPU+memory doubles cost; over-provisioning wastes money

## Common Mistakes

1. **Over-provisioning from day 1** - Starting with 4096 CPU / 8192 memory "to be safe" wastes money. Start small, scale based on actual metrics.
2. **Not monitoring CloudWatch metrics before scaling** - Guessing resource needs without data. Always check CPU/memory utilization first.
3. **Setting desiredCount=1 (no high availability)** - Single task = downtime during deployments. Use minCount=2 for HA.
4. **Using invalid CPU/memory combinations** - Fargate rejects invalid pairs (e.g., 512 CPU + 4096 memory). See valid combinations table.
5. **Scaling up when the problem is inefficient code** - Throwing more CPU at a bug. Profile code first, optimize hot paths, then scale.

## More Detail

- [docs/concepts.md](docs/concepts.md) - vCPU definition, memory limits, Fargate constraints, auto-scaling strategies
- [docs/patterns.md](docs/patterns.md) - Sizing examples, CloudWatch monitoring, when to scale up vs scale out
