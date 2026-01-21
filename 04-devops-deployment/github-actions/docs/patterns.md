# Common Patterns

## Overview

This document covers common patterns and best practices for GitHub Actions workflows.

## Pattern 1: Efficient Caching

### When to Use

When builds have dependencies that don't change often (npm packages, pip packages, go modules).

### Implementation

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Python with pip cache
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'  # Built-in caching

      # Or manual cache
      - uses: actions/cache@v4
        with:
          path: |
            ~/.cache/pip
            .venv
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      # Node with npm cache
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      # Go with module cache
      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'
          cache: true
```

### Cache Key Strategy

```yaml
# Good: Invalidates when dependencies change
key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

# Better: Include Python version
key: ${{ runner.os }}-py${{ matrix.python }}-${{ hashFiles('**/requirements.txt') }}

# Restore from partial match if exact not found
restore-keys: |
  ${{ runner.os }}-py${{ matrix.python }}-
  ${{ runner.os }}-
```

## Pattern 2: Artifacts for Job Communication

### When to Use

When you need to pass files between jobs (build outputs, test results, coverage reports).

### Implementation

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm run build

      # Upload build output
      - uses: actions/upload-artifact@v4
        with:
          name: build-output
          path: dist/
          retention-days: 7

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      # Download from previous job
      - uses: actions/download-artifact@v4
        with:
          name: build-output
          path: dist/

      - run: ./deploy.sh dist/
```

### Multiple Artifacts

```yaml
# Upload multiple artifacts
- uses: actions/upload-artifact@v4
  with:
    name: test-results-${{ matrix.os }}
    path: |
      test-results/
      coverage/

# Download all artifacts
- uses: actions/download-artifact@v4
  with:
    path: all-artifacts/
```

## Pattern 3: Reusable Workflows

### When to Use

When multiple repositories need the same workflow logic (organization standards, common patterns).

### Implementation

```yaml
# .github/workflows/reusable-ci.yml (in shared repo)
name: Reusable CI

on:
  workflow_call:
    inputs:
      python-version:
        description: 'Python version'
        required: false
        default: '3.12'
        type: string
      run-lint:
        description: 'Run linting'
        required: false
        default: true
        type: boolean
    secrets:
      CODECOV_TOKEN:
        required: false

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ inputs.python-version }}

      - name: Lint
        if: inputs.run-lint
        run: ruff check .

      - name: Test
        run: pytest --cov

      - name: Upload coverage
        if: secrets.CODECOV_TOKEN
        uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
```

```yaml
# .github/workflows/ci.yml (in calling repo)
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  ci:
    uses: org/shared-workflows/.github/workflows/reusable-ci.yml@main
    with:
      python-version: '3.12'
      run-lint: true
    secrets:
      CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```

## Pattern 4: Environment-Based Deployments

### When to Use

When you need approval gates, environment-specific secrets, or deployment history.

### Implementation

```yaml
jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://staging.example.com

    steps:
      - uses: actions/checkout@v4
      - name: Deploy to staging
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        run: ./deploy.sh staging

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://example.com

    steps:
      - uses: actions/checkout@v4
      - name: Deploy to production
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        run: ./deploy.sh production
```

Environment features:
- **Protection rules**: Required reviewers, wait timers
- **Deployment branches**: Limit which branches can deploy
- **Secrets**: Environment-specific credentials
- **URLs**: Track deployment endpoints

## Pattern 5: Composite Actions

### When to Use

When you have common steps used across multiple workflows in the same repository.

### Implementation

```yaml
# .github/actions/setup-project/action.yml
name: 'Setup Project'
description: 'Set up Python environment and install dependencies'

inputs:
  python-version:
    description: 'Python version'
    required: false
    default: '3.12'

runs:
  using: 'composite'
  steps:
    - uses: actions/setup-python@v5
      with:
        python-version: ${{ inputs.python-version }}

    - name: Install UV
      shell: bash
      run: pip install uv

    - name: Install dependencies
      shell: bash
      run: uv sync

    - name: Set up pre-commit
      shell: bash
      run: pre-commit install
```

```yaml
# .github/workflows/ci.yml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: ./.github/actions/setup-project
        with:
          python-version: '3.12'

      - run: pytest
```

## Pattern 6: FSD Deployment Workflow

### When to Use

When deploying containerized services to ECS using FSD CLI. Automates build → push to ECR → deploy pipeline.

### Implementation

```yaml
# .github/workflows/deploy.yml
name: Deploy to ECS

on:
  push:
    branches:
      - staging   # Auto-deploy staging
      - main      # Auto-deploy production

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY: my-service
  SERVICE_NAME: my-service

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build, tag, and push image to Amazon ECR
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

      - name: Install FSD CLI
        run: |
          curl -fsSL https://fsd.fetch.com/install.sh | sh
          echo "$HOME/.fsd/bin" >> $GITHUB_PATH

      - name: Deploy to staging
        if: github.ref == 'refs/heads/staging'
        run: |
          fsd deploy ${{ env.SERVICE_NAME }}.yml --env staging

      - name: Deploy to production
        if: github.ref == 'refs/heads/main'
        run: |
          fsd deploy ${{ env.SERVICE_NAME }}.yml --env prod

      - name: Notify on failure
        if: failure()
        run: |
          echo "Deployment failed! Check logs in GitHub Actions."
```

### Branch-Based Deployment Strategy

```yaml
# Option 1: Separate workflows for each environment
# .github/workflows/deploy-staging.yml
on:
  push:
    branches: [staging]

jobs:
  deploy:
    environment: staging  # Requires GitHub environment setup
    steps:
      - run: fsd deploy my-service.yml --env staging

# .github/workflows/deploy-production.yml
on:
  push:
    branches: [main]

jobs:
  deploy:
    environment: production  # Add approval gate in GitHub settings
    steps:
      - run: fsd deploy my-service.yml --env prod
```

### With Testing Before Deploy

```yaml
name: CI/CD

on:
  push:
    branches: [staging, main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      - run: pip install -r requirements.txt
      - run: pytest

  deploy:
    needs: test  # Only deploy if tests pass
    if: github.event_name == 'push'  # Skip deploy on PRs
    runs-on: ubuntu-latest
    steps:
      # ... (same as above)
```

### With Docker Build Caching

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: |
      ${{ steps.login-ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:${{ github.sha }}
      ${{ steps.login-ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:latest
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

### Required GitHub Secrets

Set these in GitHub repository settings (Settings → Secrets and variables → Actions):

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | IAM user access key with ECR and ECS permissions |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key |

**Required IAM permissions:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecs:UpdateService",
        "ecs:DescribeServices",
        "ecs:DescribeTasks"
      ],
      "Resource": "*"
    }
  ]
}
```

### Pitfalls

**Pitfall 1: Not tagging with commit SHA**
```yaml
# Bad - always uses :latest (can't track which version is deployed)
docker tag my-service:latest $ECR_REGISTRY/my-service:latest

# Good - tag with commit SHA for traceability
docker tag my-service:latest $ECR_REGISTRY/my-service:${{ github.sha }}
docker tag my-service:latest $ECR_REGISTRY/my-service:latest  # Also push latest
```

**Pitfall 2: Deploying on every PR**
```yaml
# Bad - deploys on PR (wastes resources, may conflict)
on:
  pull_request:

# Good - only deploy on push to main/staging
on:
  push:
    branches: [staging, main]
```

**Pitfall 3: Not checking FSD CLI exit code**
```yaml
# Bad - continues even if deployment fails
- run: fsd deploy my-service.yml --env staging || true

# Good - fail workflow if deployment fails
- run: fsd deploy my-service.yml --env staging
```

### Related Patterns

- **Pattern 1: Caching** - Speed up Docker builds with layer caching
- **Pattern 4: Environments** - Add approval gates for production deploys
- See `deploying-your-first-service` skill for end-to-end deployment guide

---

## Anti-Patterns

### Anti-Pattern 1: Unpinned Action Versions

```yaml
# Bad - may break unexpectedly
- uses: actions/checkout@main
- uses: actions/checkout@v4.1.0  # Too specific

# Good - major version pinning
- uses: actions/checkout@v4
```

### Anti-Pattern 2: Secrets in Logs

```yaml
# Bad - secret visible in logs
- run: echo "Key is ${{ secrets.API_KEY }}"
- run: curl -H "Authorization: ${{ secrets.TOKEN }}" ...

# Good - use env variables
- run: ./script.sh
  env:
    API_KEY: ${{ secrets.API_KEY }}
```

### Anti-Pattern 3: Duplicate Checkout

```yaml
# Bad - checking out twice
- uses: actions/checkout@v4
- uses: actions/checkout@v4  # Unnecessary

# Good - checkout once at the start
- uses: actions/checkout@v4
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| Speed up builds | Pattern 1: Caching |
| Share files between jobs | Pattern 2: Artifacts |
| Organization standards | Pattern 3: Reusable Workflows |
| Production deployments | Pattern 4: Environments |
| Common repo steps | Pattern 5: Composite Actions |
| Deploy to ECS with FSD | Pattern 6: FSD Deployment Workflow |
