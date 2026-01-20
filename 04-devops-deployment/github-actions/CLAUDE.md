# CLAUDE.md - GitHub Actions

This skill teaches CI/CD workflow creation with GitHub Actions for automated testing, building, and deployment.

## Key Concepts

- **Workflows**: YAML files defining automated processes
- **Jobs**: Independent units of work within a workflow
- **Steps**: Individual tasks within a job
- **Actions**: Reusable units (from marketplace or custom)
- **Triggers**: Events that start workflows
- **Matrix**: Multi-configuration testing
- **Secrets**: Secure credential storage

## Common Commands

```bash
make lint          # Validate workflow YAML syntax
make examples      # Show example workflows
make test-local    # Test with act (local runner)
make validate      # Run actionlint
```

## Project Structure

```
github-actions/
├── README.md
├── CLAUDE.md
├── Makefile
├── examples/
│   ├── 01-basic-ci/
│   │   └── ci.yml
│   ├── 02-docker-build/
│   │   └── docker.yml
│   └── 03-reusable-workflow/
│       ├── reusable.yml
│       └── caller.yml
├── exercises/
│   ├── exercise-1/
│   ├── exercise-2/
│   ├── exercise-3/
│   └── solutions/
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Basic CI Workflow
```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: pytest
```

### Pattern 2: Matrix Build
```yaml
jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest]
        version: ['3.11', '3.12']
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.version }}
```

### Pattern 3: Docker Build and Push
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
```

### Pattern 4: Caching
```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cache/pip
      .venv
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

## Common Mistakes

1. **Using `@main` or `@master` for actions**
   - Breaks when action updates
   - Always use version tags like `@v4`

2. **Hardcoding secrets**
   - Never put secrets in workflow files
   - Use `${{ secrets.SECRET_NAME }}`

3. **Not using `fail-fast: false` in matrix**
   - One failure cancels all jobs
   - Set to false to see all failures

4. **Missing permissions**
   - Default permissions may be insufficient
   - Explicitly declare needed permissions

## When Users Ask About...

### "How do I trigger on multiple events?"
```yaml
on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:  # Manual trigger
```

### "How do I pass data between jobs?"
Use artifacts or outputs:
```yaml
jobs:
  build:
    outputs:
      version: ${{ steps.version.outputs.value }}
    steps:
      - id: version
        run: echo "value=1.0.0" >> $GITHUB_OUTPUT
```

### "How do I run on schedule?"
```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight UTC
```

### "How do I deploy to different environments?"
Use environments with protection rules:
```yaml
jobs:
  deploy:
    environment: production
    runs-on: ubuntu-latest
```

### "How do I debug workflow failures?"
1. Check workflow run logs in GitHub UI
2. Use `act` for local testing
3. Add debug logging: `ACTIONS_RUNNER_DEBUG: true`
4. Use `tmate` action for SSH access

## Testing Workflows Locally

Use `act` (https://github.com/nektos/act):
```bash
# Install
brew install act

# Run default event
act

# Run specific event
act push

# Run specific job
act -j build

# Use secrets
act --secret-file .secrets
```

## Security Best Practices

1. **Minimize permissions**
```yaml
permissions:
  contents: read
  packages: write
```

2. **Pin action versions**
```yaml
- uses: actions/checkout@v4  # Not @main
```

3. **Use environments for deployments**
```yaml
environment:
  name: production
  url: https://example.com
```

4. **Limit secret access**
- Use repository secrets for repo-specific
- Use organization secrets for shared

## Dependencies

Key tools:
- GitHub CLI: `gh`
- Act: Local workflow runner
- actionlint: Workflow linter
