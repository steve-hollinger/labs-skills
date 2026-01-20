# Example 1: Basic CI Pipeline

This example demonstrates a comprehensive CI workflow for Python projects.

## Features

- **Linting**: Ruff for linting and formatting, MyPy for type checking
- **Testing**: pytest with coverage reporting
- **Building**: Package build verification
- **Security**: Bandit and safety scans
- **Caching**: pip dependency caching
- **Artifacts**: Coverage reports and build outputs
- **Concurrency**: Cancels duplicate runs

## Workflow Structure

```
lint ──────► test ──────► build
   │
security (parallel)
```

## Key Patterns Demonstrated

1. **Concurrency control** - Cancel in-progress runs for same branch
2. **Job dependencies** - `needs: lint` ensures order
3. **Caching** - `cache: 'pip'` speeds up dependency installation
4. **Artifacts** - Upload coverage and build outputs
5. **Continue on error** - Security scan warns but doesn't fail

## Usage

Copy `ci.yml` to `.github/workflows/ci.yml` in your repository.

## Customization

- Change `PYTHON_VERSION` to your target version
- Add more jobs for additional checks
- Adjust `paths` filter to limit triggers
