# Common Patterns

## Overview

This document covers common patterns and best practices for writing CLAUDE.md files that effectively guide AI assistants.

## Pattern 1: The Standard Structure

### When to Use

Every CLAUDE.md file should follow a consistent structure. Use this pattern as your starting point.

### Implementation

```markdown
# CLAUDE.md - [Project/Component Name]

Brief one-line description of what this is.

## Overview

2-3 sentences explaining:
- What this project/component does
- Why it exists
- Who uses it

## Key Commands

```bash
make setup    # One-line description
make test     # One-line description
make build    # One-line description
```

## Architecture

Key architectural decisions and why they were made.

## Code Patterns

### Pattern Name
```code
Example implementation
```

## Common Mistakes

1. **Mistake description**
   - Why it happens
   - How to fix it

## When Users Ask About...

### "Common question?"
Direct, actionable answer.
```

### Example

See Example 1 in this skill for a complete, working example.

### Pitfalls to Avoid

- Don't include every possible section - only what's relevant
- Don't duplicate information from README.md
- Don't include temporary information (current sprint goals, etc.)

## Pattern 2: The Decision Record

### When to Use

When you need to document why certain architectural decisions were made, so AI doesn't suggest reversing them.

### Implementation

```markdown
## Architecture Decisions

### ADR-001: Use PostgreSQL over MongoDB

**Status:** Accepted
**Context:** We needed a database for user data with complex relationships.
**Decision:** PostgreSQL with SQLAlchemy ORM.
**Consequences:**
- Strong consistency guarantees
- Requires migrations for schema changes
- Team has existing PostgreSQL expertise

**Note to AI:** Do not suggest switching to MongoDB or other NoSQL databases.
This decision was made deliberately after evaluating both options.
```

### Example

```python
# CLAUDE.md section for a service that chose gRPC over REST

ARCHITECTURE_DECISION = """
### Why gRPC Instead of REST

We use gRPC for service-to-service communication because:
1. Type-safe contracts via Protocol Buffers
2. Bi-directional streaming for real-time features
3. Better performance for internal service calls

REST is still used for:
- Public APIs (easier client integration)
- Simple CRUD endpoints with no streaming needs

**AI Guidance:** When adding new internal service calls, use gRPC.
When adding public endpoints, use REST.
"""
```

### Pitfalls to Avoid

- Don't document every micro-decision
- Don't include decisions that may change soon
- Don't forget to update when decisions are reversed

## Pattern 3: The Error Dictionary

### When to Use

When your codebase has specific error handling patterns or common error scenarios that AI should understand.

### Implementation

```markdown
## Common Errors and Solutions

### "Connection refused on port 5432"
**Cause:** PostgreSQL is not running
**Solution:** Run `make db-start` or `docker-compose up -d postgres`

### "ModuleNotFoundError: xyz"
**Cause:** Dependencies not installed
**Solution:** Run `make setup` to install all dependencies

### Tests failing with "fixture not found"
**Cause:** Running pytest from wrong directory
**Solution:** Always run `make test` from project root
```

### Example

```python
ERROR_DICTIONARY = {
    "ECONNREFUSED": {
        "cause": "Target service is not running",
        "solutions": [
            "Check if service is started: `docker-compose ps`",
            "Check service logs: `docker-compose logs <service>`",
            "Restart service: `docker-compose restart <service>`"
        ]
    },
    "JWT_EXPIRED": {
        "cause": "Authentication token has expired",
        "solutions": [
            "For testing: generate new token with `make auth-token`",
            "For production: refresh token using /auth/refresh endpoint"
        ]
    }
}
```

### Pitfalls to Avoid

- Don't include errors that are self-explanatory
- Don't forget to update when error messages change
- Don't include sensitive information in error solutions

## Pattern 4: The Context Switch

### When to Use

When a subdirectory has significantly different conventions than the parent project.

### Implementation

```markdown
# CLAUDE.md - Legacy Module

**CONTEXT SWITCH:** This module uses different conventions than the rest
of the project. Follow the patterns below, NOT the root CLAUDE.md.

## Why Different

This module was acquired from Company X and hasn't been migrated yet.
It uses:
- CamelCase for functions (project standard is snake_case)
- Callbacks instead of async/await
- Custom logging instead of structlog

## Working in This Module

When modifying this code:
1. Follow existing patterns (CamelCase, callbacks)
2. Don't introduce new patterns from the main codebase
3. Add TODOs for future migration where appropriate

## Migration Status

- [ ] Convert to async/await
- [ ] Adopt project naming conventions
- [ ] Switch to structlog
```

### Example

```python
# For a monorepo with different languages

# Root CLAUDE.md
ROOT_GUIDANCE = """
This is a polyglot monorepo. Each service has its own conventions.
Always check the service's CLAUDE.md before making changes.
"""

# services/python-api/CLAUDE.md
PYTHON_GUIDANCE = """
**Language:** Python 3.11
**Framework:** FastAPI
**Style:** Black formatter, isort, mypy strict
"""

# services/go-worker/CLAUDE.md
GO_GUIDANCE = """
**Language:** Go 1.21
**Style:** gofmt, golangci-lint
**Note:** This service handles background jobs, not HTTP requests
"""
```

### Pitfalls to Avoid

- Don't create unnecessary context switches
- Do explain WHY the context is different
- Don't let legacy patterns spread to new code

## Pattern 5: The FAQ Section

### When to Use

When there are common questions that AI might ask or assumptions it might make incorrectly.

### Implementation

```markdown
## When AI Asks About...

### "Should I add error handling here?"
Yes, always wrap external calls (database, API, filesystem) in try/except.
Use our custom exceptions from `app.exceptions`.

### "What testing framework should I use?"
pytest only. We don't use unittest. All tests go in `tests/` directory.

### "Should I add logging?"
Yes, use structlog. Import: `from app.logging import get_logger`
Log at INFO level for normal operations, ERROR for failures.

### "Can I add a new dependency?"
Check if similar functionality exists in current dependencies first.
If new dep is needed, add to pyproject.toml with minimum version pin.
```

### Example

```python
FAQ_SECTION = """
## Frequently Anticipated Questions

### "Why are there two user tables?"
`users` is for authentication data (email, password hash).
`user_profiles` is for display data (name, avatar, preferences).
They're separate for security isolation. Don't merge them.

### "Should I write unit or integration tests?"
Write both. Unit tests for business logic, integration tests for endpoints.
Target: 80% unit test coverage, integration tests for all API endpoints.

### "How do I add a new API endpoint?"
1. Add route in `app/routes/<domain>.py`
2. Add handler in `app/handlers/<domain>.py`
3. Add tests in `tests/api/test_<domain>.py`
4. Update OpenAPI schema if adding new models
"""
```

### Pitfalls to Avoid

- Don't include questions with obvious answers
- Don't make the FAQ section too long (top 5-10 questions)
- Do update based on actual AI confusion patterns

## Anti-Patterns

### Anti-Pattern 1: The Novel

CLAUDE.md files that are thousands of lines long and try to document everything.

```markdown
# Bad - Too much irrelevant detail
## Complete History of the Project
In 2019, our founder had a vision...
[500 lines of history]

## Every Library We Evaluated
We looked at Django, Flask, FastAPI, Starlette...
[Detailed comparisons nobody needs]
```

### Better Approach

```markdown
# Good - Focused and relevant
## Overview
User authentication service built with FastAPI.

## Key Decision
FastAPI over Flask for async support and automatic OpenAPI docs.
```

### Anti-Pattern 2: The Wishlist

Documenting aspirational patterns that don't exist in the codebase.

```markdown
# Bad - Aspirational, not actual
## Testing
We have comprehensive E2E tests for all user journeys.
[In reality: 5% test coverage]
```

### Better Approach

```markdown
# Good - Honest and actionable
## Testing
Current coverage: ~30% unit tests.
Priority areas for new tests: authentication, payment processing.
Pattern for new tests: see tests/unit/test_auth.py as example.
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| New project | Standard Structure |
| Explaining past decisions | Decision Record |
| Complex error scenarios | Error Dictionary |
| Legacy/acquired code | Context Switch |
| Preventing common AI mistakes | FAQ Section |
| Large monorepo | Hierarchy with all patterns |
