# Solution 3: Deployment Pipeline

## Key Features

### 1. Environment Configuration

```yaml
deploy-staging:
  environment:
    name: staging
    url: https://staging.example.com
```

This:
- Tracks deployments in GitHub UI
- Enables environment-specific secrets
- Shows deployment URL in Actions

### 2. Production Approval

Configure in GitHub Settings > Environments > production:
- Add required reviewers
- Optionally add wait timer
- Restrict deployment branches

### 3. Environment Secrets

```yaml
env:
  DEPLOY_KEY: ${{ secrets.STAGING_DEPLOY_KEY }}
```

Each environment can have its own secrets:
- `staging`: `STAGING_DEPLOY_KEY`
- `production`: `PRODUCTION_DEPLOY_KEY`

### 4. Concurrency Control

```yaml
concurrency:
  group: deploy-${{ github.ref }}
  cancel-in-progress: false
```

Prevents multiple deployments running simultaneously.

### 5. Pipeline Flow

```
build ──► test ──► deploy-staging ──► smoke-test ──► deploy-production
                                                          │
                                                    [Requires Approval]
```

## GitHub Configuration

### Create Environments

1. Go to repository Settings
2. Click "Environments" in sidebar
3. Create `staging` environment
4. Create `production` environment with:
   - Required reviewers: Add team members
   - Wait timer: Optional (e.g., 5 minutes)
   - Deployment branches: Only `main`

### Add Secrets

For each environment:
1. Click environment name
2. Click "Add secret"
3. Add `STAGING_DEPLOY_KEY` / `PRODUCTION_DEPLOY_KEY`

## Production Approval Process

1. Workflow reaches `deploy-production` job
2. GitHub shows "Waiting for approval"
3. Designated reviewers receive notification
4. Reviewer clicks "Review deployments"
5. Reviewer approves or rejects
6. If approved, job continues

## Benefits

- **Safety**: Human approval before production
- **Visibility**: Track all deployments in GitHub
- **Security**: Isolated secrets per environment
- **Traceability**: Link commits to deployments
