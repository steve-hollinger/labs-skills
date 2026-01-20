# Core Concepts

## Overview

GitHub Actions is a CI/CD platform that allows you to automate build, test, and deployment pipelines directly in your GitHub repository.

## Concept 1: Workflows

### What It Is

A workflow is an automated process defined in a YAML file in `.github/workflows/`. Each workflow can contain multiple jobs that run in response to events.

### Why It Matters

- **Automation**: Runs tasks automatically on code changes
- **Consistency**: Same process every time
- **Visibility**: Results visible in GitHub UI
- **Integration**: Deep GitHub integration (PRs, issues, releases)

### How It Works

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

# Triggers
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

# Jobs to run
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: npm run build

  test:
    runs-on: ubuntu-latest
    needs: build  # Run after build
    steps:
      - uses: actions/checkout@v4
      - name: Test
        run: npm test
```

Workflow components:
- `name`: Display name in GitHub UI
- `on`: Events that trigger the workflow
- `jobs`: Independent units of work

## Concept 2: Events and Triggers

### What It Is

Events are specific activities that trigger a workflow run. GitHub provides dozens of event types from code pushes to issue comments.

### Why It Matters

- **Flexibility**: Run workflows on exactly the events you need
- **Efficiency**: Don't run unnecessary builds
- **Control**: Different workflows for different scenarios

### How It Works

```yaml
on:
  # Code events
  push:
    branches: [main]
    paths:
      - 'src/**'  # Only when src changes
    tags:
      - 'v*'  # On version tags

  pull_request:
    types: [opened, synchronize, reopened]

  # Scheduled (cron)
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight UTC

  # Manual trigger
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production

  # From other workflows
  workflow_call:
    inputs:
      config:
        required: true
        type: string

  # Repository events
  release:
    types: [published]

  issue_comment:
    types: [created]
```

Common event types:
| Event | Trigger |
|-------|---------|
| `push` | Code pushed to branch |
| `pull_request` | PR opened/updated |
| `schedule` | Cron schedule |
| `workflow_dispatch` | Manual run |
| `release` | Release published |
| `workflow_call` | Called by another workflow |

## Concept 3: Jobs and Steps

### What It Is

Jobs are independent units of work that run on a runner. Steps are individual tasks within a job that run sequentially.

### Why It Matters

- **Parallelism**: Independent jobs run in parallel
- **Dependencies**: Control execution order with `needs`
- **Isolation**: Each job has a fresh environment
- **Reuse**: Steps can use community actions

### How It Works

```yaml
jobs:
  # Job 1: Lint
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm run lint

  # Job 2: Test (runs in parallel with lint)
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm test

  # Job 3: Build (waits for lint and test)
  build:
    needs: [lint, test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm run build

  # Job 4: Deploy (waits for build)
  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - run: ./deploy.sh
```

Job execution flow:
```
┌────────┐     ┌────────┐
│  lint  │     │  test  │
└────┬───┘     └────┬───┘
     │              │
     └──────┬───────┘
            │
       ┌────▼────┐
       │  build  │
       └────┬────┘
            │
       ┌────▼────┐
       │ deploy  │
       └─────────┘
```

## Concept 4: Matrix Builds

### What It Is

Matrix builds allow you to run a job multiple times with different configurations (OS, language version, etc.).

### Why It Matters

- **Coverage**: Test across multiple environments
- **Efficiency**: All matrix jobs run in parallel
- **Maintainability**: Single job definition for many configs

### How It Works

```yaml
jobs:
  test:
    strategy:
      fail-fast: false  # Don't cancel on first failure
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python: ['3.10', '3.11', '3.12']
        exclude:
          - os: windows-latest
            python: '3.10'
        include:
          - os: ubuntu-latest
            python: '3.12'
            coverage: true

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}

      - name: Run tests
        run: pytest

      - name: Upload coverage
        if: matrix.coverage
        run: codecov
```

Matrix creates combinations:
- ubuntu-latest + 3.10, 3.11, 3.12
- macos-latest + 3.10, 3.11, 3.12
- windows-latest + 3.11, 3.12 (3.10 excluded)

## Concept 5: Secrets and Security

### What It Is

Secrets are encrypted environment variables that store sensitive data like API keys, passwords, and tokens.

### Why It Matters

- **Security**: Secrets never appear in logs
- **Access Control**: Scoped to repo/org/environment
- **Compliance**: Meets security requirements

### How It Works

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production  # Use environment secrets

    steps:
      - name: Deploy
        env:
          # Repository secret
          API_KEY: ${{ secrets.API_KEY }}
          # Built-in token
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          # Environment secret
          AWS_ACCESS_KEY: ${{ secrets.AWS_ACCESS_KEY_ID }}
        run: ./deploy.sh

      - name: Configure AWS
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
```

Secret types:
1. **Repository secrets**: Available to all workflows in repo
2. **Organization secrets**: Shared across org repos
3. **Environment secrets**: Available only in specific environment
4. **GITHUB_TOKEN**: Auto-generated, scoped to repo

Security best practices:
- Use environments with protection rules
- Minimize secret scope
- Rotate secrets regularly
- Never echo secrets in logs

## Summary

Key takeaways:

1. **Workflows** are YAML files that define automated processes
2. **Events** trigger workflows on specific GitHub activities
3. **Jobs** run independently; **steps** run sequentially within jobs
4. **Matrix builds** test across multiple configurations efficiently
5. **Secrets** provide secure storage for sensitive data
