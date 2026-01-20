# Solution 2: Caching and Artifacts

## Key Optimizations

### 1. Built-in Pip Caching

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: 'pip'
```

This automatically caches `~/.cache/pip` based on `requirements.txt`.

### 2. Artifact Upload

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: build-output
    path: dist/
    retention-days: 7
```

### 3. Artifact Download

```yaml
- uses: actions/download-artifact@v4
  with:
    name: build-output
    path: dist/
```

### 4. Conditional Upload

```yaml
- uses: actions/upload-artifact@v4
  if: always()  # Upload even if tests fail
```

### 5. Multiple Files

```yaml
path: |
  test-results.xml
  coverage.xml
```

## Cache Behavior

- **First run**: Cache miss, installs from PyPI (~30s)
- **Subsequent runs**: Cache hit, uses cached packages (~5s)
- **Cache invalidation**: When requirements.txt changes

## Artifacts vs Cache

| Feature | Cache | Artifacts |
|---------|-------|-----------|
| Purpose | Speed up installs | Share between jobs |
| Retention | 7 days (configurable) | 90 days default |
| Scope | Same workflow key | Download anywhere |
| Size limit | 10GB per repo | 500MB per artifact |

## Time Savings

| Job | Without Cache | With Cache |
|-----|---------------|------------|
| Build | 45s | 15s |
| Test | 40s | 12s |
| Lint | 20s | 8s |
| **Total** | ~105s | ~35s |
