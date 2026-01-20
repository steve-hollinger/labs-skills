# Exercise 2: Caching and Artifacts

## Objective

Optimize a slow CI workflow by implementing effective caching and artifact management.

## Problem

The provided workflow is slow because:
- Dependencies are downloaded fresh every run
- Build outputs are not shared between jobs
- Test results are lost after workflow completes

## Requirements

1. **Implement caching**
   - Cache pip dependencies
   - Cache npm packages
   - Cache build outputs

2. **Use artifacts**
   - Upload build output from build job
   - Download in test job
   - Upload test results for later analysis

3. **Optimize build**
   - Don't rebuild if cache hit
   - Share artifacts between jobs

## Starting Files

- `ci.yml` - Slow workflow to optimize
- `app/` - Application code

## Steps

1. Add pip caching using setup-python's built-in cache

2. Add manual caching for build outputs

3. Implement artifact upload/download between jobs

4. Add test result artifact upload

## Cache Key Best Practices

```yaml
# Good: Invalidates when dependencies change
key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

# With restore fallback
restore-keys: |
  ${{ runner.os }}-pip-
```

## Expected Improvement

- First run: ~3 minutes (cold cache)
- Subsequent runs: ~1 minute (warm cache)

## Success Criteria

- [ ] Dependencies cached correctly
- [ ] Build outputs shared between jobs
- [ ] Test results available as artifacts
- [ ] Build times reduced significantly
