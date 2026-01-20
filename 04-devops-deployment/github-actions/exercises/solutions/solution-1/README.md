# Solution 1: Multi-Language CI Pipeline

## Key Features

### 1. Matrix Configuration

```yaml
strategy:
  fail-fast: false  # Continue other jobs if one fails
  matrix:
    os: [ubuntu-latest, macos-latest]
    python: ['3.11', '3.12']
```

This creates 4 job combinations for Python and 4 for Node.

### 2. Built-in Caching

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: ${{ matrix.python }}
    cache: 'pip'
    cache-dependency-path: backend/requirements.txt
```

Using the built-in cache is simpler than manual caching.

### 3. Matrix Variables

```yaml
runs-on: ${{ matrix.os }}
python-version: ${{ matrix.python }}
```

Access matrix values with `${{ matrix.VARIABLE }}`.

### 4. Artifact Naming

```yaml
name: python-test-results-${{ matrix.os }}-${{ matrix.python }}
```

Unique names prevent artifact conflicts in matrix jobs.

### 5. Job Dependencies

```yaml
integration:
  needs: [python-test, node-test]
```

Integration job waits for all matrix jobs to complete.

## Total Jobs

- Python: 2 OS x 2 versions = 4 jobs
- Node: 2 OS x 2 versions = 4 jobs
- Integration: 1 job
- **Total: 9 jobs**

## Job Flow

```
python-test (4x parallel)  ──┐
                             ├──► integration
node-test (4x parallel)    ──┘
```
