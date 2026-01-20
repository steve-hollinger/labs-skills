# Exercise 1: Multi-Language CI Pipeline

## Objective

Create a CI pipeline that tests a project with both Python and Node.js components using matrix builds.

## Requirements

Your workflow must:

1. **Matrix configuration**
   - Test on Ubuntu and macOS
   - Test Python 3.11 and 3.12
   - Test Node.js 18 and 20

2. **Jobs**
   - `python-test`: Test Python code with pytest
   - `node-test`: Test Node.js code with Jest
   - `integration`: Run integration tests (after both pass)

3. **Caching**
   - Cache pip dependencies
   - Cache npm dependencies

4. **Artifacts**
   - Upload test results from both languages

## Starting Files

- `ci.yml` - Incomplete workflow to complete
- `backend/` - Python application
- `frontend/` - Node.js application

## Steps

1. Complete the matrix configuration for both Python and Node jobs

2. Add proper caching for dependencies

3. Set up job dependencies so integration tests run last

4. Add artifact uploads for test results

5. Test your workflow (use `act` for local testing)

## Expected Job Flow

```
┌─────────────┐     ┌─────────────┐
│ python-test │     │  node-test  │
│ (2x2 matrix)│     │ (2x2 matrix)│
└──────┬──────┘     └──────┬──────┘
       │                   │
       └─────────┬─────────┘
                 │
         ┌───────▼───────┐
         │  integration  │
         └───────────────┘
```

## Success Criteria

- [ ] Matrix builds for both Python and Node
- [ ] Dependencies cached correctly
- [ ] Integration tests run after unit tests
- [ ] Test results uploaded as artifacts
- [ ] All matrix combinations run
