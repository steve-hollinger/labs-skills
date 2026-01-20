# GitHub Actions

Master CI/CD workflow creation with GitHub Actions for automated testing, building, and deployment.

## Learning Objectives

After completing this skill, you will be able to:
- Create and configure GitHub Actions workflows
- Implement matrix builds for multi-version testing
- Use caching to speed up builds
- Manage artifacts and releases
- Create reusable workflows and composite actions
- Implement secure deployment pipelines

## Prerequisites

- GitHub account with repository access
- Basic YAML syntax understanding
- Familiarity with CI/CD concepts
- Completed [Docker/ECR](../docker-ecr/) skill recommended

## Quick Start

```bash
# Validate workflow syntax
make lint

# View example workflows
make examples

# Run act for local testing (if installed)
make test-local
```

## Concepts

### Workflow Structure

GitHub Actions workflows are defined in `.github/workflows/*.yml`:

```yaml
name: CI Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: pytest
```

### Matrix Builds

Test across multiple versions and platforms:

```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ['3.11', '3.12']
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
```

### Caching Dependencies

Speed up builds with dependency caching:

```yaml
- name: Cache pip packages
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

## Examples

### Example 1: Basic CI Pipeline

Standard CI workflow with linting, testing, and coverage.

See [examples/01-basic-ci/](./examples/01-basic-ci/) for the complete workflow.

### Example 2: Docker Build and Push

Build Docker images and push to registry.

See [examples/02-docker-build/](./examples/02-docker-build/) for the complete workflow.

### Example 3: Reusable Workflow

Create reusable workflows for organization-wide standards.

See [examples/03-reusable-workflow/](./examples/03-reusable-workflow/) for the complete workflow.

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Create a multi-language CI pipeline with matrix builds
2. **Exercise 2**: Implement caching and artifacts for faster builds
3. **Exercise 3**: Build a complete deployment pipeline with environments

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Not Using Specific Action Versions

```yaml
# Bad - may break unexpectedly
- uses: actions/checkout@main

# Good - pinned version
- uses: actions/checkout@v4
```

### Exposing Secrets in Logs

```yaml
# Bad - secret visible in logs
- run: echo ${{ secrets.API_KEY }}

# Good - use secret masking
- run: ./script.sh
  env:
    API_KEY: ${{ secrets.API_KEY }}
```

### Inefficient Caching

```yaml
# Bad - caches everything
key: ${{ runner.os }}-cache

# Good - cache invalidates when deps change
key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

## Key Syntax

### Triggers

```yaml
on:
  push:
    branches: [main]
    paths:
      - 'src/**'
  pull_request:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        default: 'staging'
```

### Job Dependencies

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    # ...

  test:
    needs: build
    runs-on: ubuntu-latest
    # ...

  deploy:
    needs: [build, test]
    runs-on: ubuntu-latest
    # ...
```

### Conditional Execution

```yaml
jobs:
  deploy:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    # ...

steps:
  - name: Deploy to production
    if: github.event_name == 'push' && contains(github.ref, 'tags')
    run: ./deploy.sh
```

## Further Reading

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- Related skills in this repository:
  - [Docker/ECR](../docker-ecr/)
  - [Docker Compose](../docker-compose/)
