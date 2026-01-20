# Example 3: Reusable Workflows

This example demonstrates creating and using reusable workflows for organization-wide CI standards.

## Files

- `reusable.yml` - The reusable workflow definition
- `caller.yml` - Example workflow that calls the reusable workflow

## Features

- **Configurable inputs**: Python version, runner, feature flags
- **Secrets**: Optional Codecov token
- **Outputs**: Coverage percentage returned to caller
- **Conditional jobs**: Skip lint or security based on inputs
- **Organization standards**: Consistent CI across repos

## Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `python-version` | string | '3.12' | Python version |
| `runs-on` | string | 'ubuntu-latest' | Runner |
| `run-lint` | boolean | true | Enable linting |
| `run-security` | boolean | true | Enable security scan |
| `coverage-threshold` | string | '80' | Minimum coverage |

## Outputs

| Output | Description |
|--------|-------------|
| `coverage` | Test coverage percentage |

## Usage

### Same Repository

```yaml
jobs:
  ci:
    uses: ./.github/workflows/reusable.yml
    with:
      python-version: '3.12'
```

### Different Repository

```yaml
jobs:
  ci:
    uses: org/shared-workflows/.github/workflows/reusable.yml@v1
    with:
      python-version: '3.12'
    secrets:
      CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```

## Key Patterns

1. **workflow_call trigger** - Makes workflow reusable
2. **Typed inputs** - string, boolean with defaults
3. **Secrets inheritance** - Pass secrets explicitly
4. **Job outputs** - Return values to caller
5. **Conditional execution** - `if: inputs.run-lint`

## Benefits

- **Consistency**: Same CI process across all repos
- **Maintenance**: Update once, apply everywhere
- **Flexibility**: Override defaults per-repo
- **Visibility**: Centralized standards
