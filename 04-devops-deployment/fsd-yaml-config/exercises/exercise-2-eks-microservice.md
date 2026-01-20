# Exercise 2: Write an EKS Microservice Deployment

## Objective

Create an FSD YAML configuration for an EKS-based microservice with proper resource management and autoscaling.

## Scenario

You're building a recommendation service for an e-commerce platform. The service:
- Receives product IDs and returns personalized recommendations
- Has variable traffic patterns (high during sales, low overnight)
- Needs to scale based on CPU usage
- Must have proper resource limits to prevent cluster instability

## Requirements

Create an FSD YAML file for `recommendation-service` that:

1. **Platform**: EKS

2. **Compute**:
   - Base replicas: 3
   - Resource requests: 500m CPU, 512Mi memory
   - Resource limits: 1000m CPU, 1Gi memory

3. **Autoscaling**:
   - Minimum replicas: 2
   - Maximum replicas: 15
   - Scale at 70% CPU utilization

4. **Health Probes**:
   - Readiness probe on `/ready` port 8080
   - Liveness probe on `/health` port 8080
   - Initial delay: 10 seconds

5. **Node Scheduling**:
   - Node selector: `workload-type: api`
   - Toleration for dedicated API nodes

6. **Environment Variables**:
   - `MODEL_ENDPOINT` from SSM Parameter Store at `/recommendation/model-endpoint`
   - `CACHE_TTL`: 300
   - `MAX_RECOMMENDATIONS`: 10
   - `LOG_FORMAT`: json

7. **Metadata**:
   - Team: ml-platform
   - Tags: environment=production, tier=api, cost-center=ml

## Hints

- EKS uses Kubernetes resource format: CPU in millicores ("500m"), memory with units ("512Mi")
- Autoscaling uses HPA-style configuration
- Remember both liveness and readiness probes are important

## Template

```yaml
name: recommendation-service
platform: eks
description: # Add description

team: # Add team
tags:
  # Add tags

compute:
  replicas: # Add replicas
  resources:
    requests:
      # Add requests
    limits:
      # Add limits
  autoscaling:
    # Add autoscaling config

scheduling:
  # Add node selector and tolerations

probes:
  # Add liveness and readiness probes

environment:
  # Add environment variables
```

## Validation

Test your solution:

```bash
make validate YAML=exercises/solutions/solution-2.yml
```

## Bonus Challenge

Add a pod disruption budget that ensures at least 2 pods are always available during node maintenance.

## Submit Your Solution

Save your solution to `exercises/solutions/solution-2.yml`
