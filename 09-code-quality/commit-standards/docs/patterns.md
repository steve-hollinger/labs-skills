# Conventional Commits: Real-World Patterns

This document showcases real-world commit message patterns from professional development workflows. Use these as templates for your own commits.

## Table of Contents

1. [Feature Development](#feature-development)
2. [Bug Fixes](#bug-fixes)
3. [Documentation](#documentation)
4. [Refactoring](#refactoring)
5. [Testing](#testing)
6. [DevOps and CI/CD](#devops-and-cicd)
7. [Dependency Management](#dependency-management)
8. [Breaking Changes](#breaking-changes)
9. [Multi-Step Features](#multi-step-features)
10. [Common Anti-Patterns](#common-anti-patterns)

---

## Feature Development

### Simple Feature

```
feat: add user profile avatar upload
```

### Feature with Scope

```
feat(users): add profile avatar upload

Implemented avatar upload with the following features:
- Support for JPEG, PNG, and WebP formats
- Maximum file size of 5MB
- Automatic resizing to 200x200 pixels
- S3 storage integration
```

### Feature with Technical Details

```
feat(api): implement rate limiting for public endpoints

Added rate limiting using sliding window algorithm:
- 100 requests per minute for authenticated users
- 20 requests per minute for anonymous users
- Custom X-RateLimit-* headers in responses

Uses Redis for distributed rate limit tracking.
```

### Feature Closing Issues

```
feat(checkout): add express checkout option

One-click checkout for saved payment methods.
Reduces checkout flow from 4 steps to 1.

Closes #892
Closes #901
```

---

## Bug Fixes

### Simple Bug Fix

```
fix: resolve login redirect loop on expired sessions
```

### Bug Fix with Root Cause

```
fix(auth): prevent token refresh race condition

When multiple API calls triggered simultaneously with an
expired token, each would attempt to refresh, causing
race conditions and intermittent 401 errors.

Solution: Implemented request queuing during token refresh.
All pending requests wait for a single refresh operation.

Fixes #456
```

### Bug Fix with Reproduction Steps

```
fix(cart): handle zero quantity items correctly

Previously, setting quantity to 0 would leave ghost items
in the cart that couldn't be removed.

Steps to reproduce:
1. Add item to cart
2. Update quantity to 0
3. Item remains visible but not interactive

Root cause: Quantity validation only checked for negative
values, not zero.

Fixes #789
```

### Security Bug Fix

```
fix(security): patch SQL injection in search endpoint

The search query parameter was not properly sanitized,
allowing SQL injection attacks.

Replaced string concatenation with parameterized queries.
Added input validation for search terms.

CVE: CVE-2024-12345
Severity: Critical
```

---

## Documentation

### README Update

```
docs: update installation instructions for Node 20
```

### API Documentation

```
docs(api): add authentication flow diagrams

Added sequence diagrams for:
- OAuth2 authorization code flow
- Token refresh flow
- Logout and session invalidation

Using Mermaid for diagram rendering in markdown.
```

### Code Comments

```
docs: add JSDoc comments to utility functions

Documented all exported functions in src/utils with:
- Parameter descriptions
- Return value documentation
- Usage examples
- Related function references
```

### Migration Guide

```
docs: add v2 to v3 migration guide

Comprehensive guide covering:
- Breaking changes and their solutions
- New feature adoption
- Deprecated API replacement
- Performance optimization tips

Includes code samples for all common migration scenarios.
```

---

## Refactoring

### Code Extraction

```
refactor: extract email validation into shared utility

Moved duplicate email validation logic from:
- UserService
- ContactForm
- NewsletterSignup

Into a shared validateEmail() utility function.
No behavior changes.
```

### Architecture Change

```
refactor(api): migrate from Express to Fastify

Performance improvements:
- 2x faster JSON serialization
- 40% reduction in memory usage
- Built-in schema validation

All endpoints maintain same interface.
Internal implementation only.
```

### Code Simplification

```
refactor(auth): replace callback hell with async/await

Converted 5 levels of nested callbacks to flat async/await.
No functionality changes, improved readability.

Before: 47 lines, 5 levels deep
After: 23 lines, 1 level deep
```

### Design Pattern Implementation

```
refactor(notifications): implement strategy pattern

Replaced switch statement with strategy pattern for
notification delivery methods (email, SMS, push).

Benefits:
- Easier to add new notification types
- Each strategy can be tested independently
- Open/Closed principle compliance
```

---

## Testing

### Adding Unit Tests

```
test: add unit tests for UserService.create()

Coverage increase: 45% -> 78%

New test cases:
- Valid user creation
- Duplicate email handling
- Invalid input validation
- Database error recovery
```

### Integration Tests

```
test(api): add integration tests for payment flow

End-to-end payment flow testing:
- Credit card processing
- PayPal integration
- Refund handling
- Webhook verification

Uses test payment provider sandbox.
```

### Fixing Flaky Tests

```
test: fix flaky date-dependent tests

Tests were failing intermittently due to timezone issues
and date boundary conditions.

Solution:
- Mock Date.now() in all date tests
- Use UTC consistently
- Add test fixtures with explicit timestamps
```

### Test Utilities

```
test: add factory functions for test data generation

Created test factories for common models:
- createTestUser()
- createTestOrder()
- createTestProduct()

Simplifies test setup and improves consistency.
```

---

## DevOps and CI/CD

### CI Configuration

```
ci: add GitHub Actions workflow for PR checks

Workflow runs on pull requests:
- Lint check
- Type check
- Unit tests
- Build verification

Blocks merge if any check fails.
```

### Docker Configuration

```
build: add multi-stage Dockerfile

Reduced image size from 1.2GB to 89MB using:
- Multi-stage build
- Alpine base image
- Production-only dependencies

Build time reduced by 40%.
```

### Deployment Configuration

```
ci(deploy): add staging environment workflow

Automatic deployment to staging on main branch:
- Build and push Docker image
- Update ECS service
- Run smoke tests
- Notify Slack channel

Manual approval required for production.
```

### Infrastructure Changes

```
build(terraform): add auto-scaling for API servers

Configure auto-scaling based on:
- CPU utilization > 70%
- Request count > 1000/min
- Min: 2 instances, Max: 10 instances

Includes CloudWatch alarms for monitoring.
```

---

## Dependency Management

### Security Updates

```
build(deps): update lodash to fix prototype pollution

Bump lodash from 4.17.20 to 4.17.21 to address
CVE-2021-23337 (prototype pollution vulnerability).

No breaking changes expected.
```

### Major Version Updates

```
build(deps): upgrade React from 17 to 18

Migration completed:
- Updated createRoot API
- Replaced ReactDOM.render
- Enabled concurrent features
- Updated testing utilities

All tests passing after migration.
```

### Adding Dependencies

```
build(deps): add zod for runtime schema validation

Replacing joi with zod for:
- TypeScript-first approach
- Smaller bundle size
- Better inference
- No @types package needed
```

### Removing Dependencies

```
build(deps): remove moment.js in favor of date-fns

Replaced moment.js (329KB) with date-fns (tree-shakable).
Reduced bundle size by 280KB.

Utility functions updated to use new API.
All date formatting tests passing.
```

---

## Breaking Changes

### API Breaking Change

```
feat(api)!: change pagination response format

BREAKING CHANGE: Pagination now uses cursor-based format.

Before:
{
  "data": [...],
  "page": 1,
  "totalPages": 10
}

After:
{
  "data": [...],
  "cursor": "abc123",
  "hasMore": true
}

Migration guide: docs/migration/pagination.md
```

### Configuration Breaking Change

```
feat(config)!: require explicit database URL

BREAKING CHANGE: DATABASE_URL environment variable is now required.

Previously defaulted to localhost which caused silent failures
in production deployments.

Update your .env files with explicit database connection strings.
```

### Removal of Deprecated API

```
refactor(api)!: remove deprecated v1 endpoints

BREAKING CHANGE: All /api/v1/* endpoints have been removed.

Deprecated since v2.0.0 (18 months ago).
Migrate to /api/v2/* endpoints.

Removed endpoints:
- /api/v1/users (use /api/v2/users)
- /api/v1/orders (use /api/v2/orders)
- /api/v1/products (use /api/v2/products)
```

### Type Change

```
feat(types)!: change userId from number to UUID

BREAKING CHANGE: User IDs are now UUIDs instead of auto-increment integers.

Migration:
1. Run migration script: npm run migrate:user-ids
2. Update client applications to handle UUID format
3. Update foreign key references

Database migration handles existing data automatically.
```

---

## Multi-Step Features

When implementing a large feature across multiple commits:

### Step 1: Database Schema

```
feat(db): add tables for notification preferences

Schema for user notification settings:
- notification_preferences table
- notification_channels table
- user_notification_settings table

Part 1 of 4: Notification system implementation
Related: #500
```

### Step 2: Backend API

```
feat(api): add notification preferences endpoints

RESTful endpoints:
- GET /users/:id/notifications
- PUT /users/:id/notifications
- POST /users/:id/notifications/test

Part 2 of 4: Notification system implementation
Related: #500
```

### Step 3: Service Layer

```
feat(notifications): implement notification delivery service

Multi-channel delivery support:
- Email via SendGrid
- SMS via Twilio
- Push via Firebase

Part 3 of 4: Notification system implementation
Related: #500
```

### Step 4: UI Integration

```
feat(ui): add notification preferences page

User interface for managing notifications:
- Channel toggle switches
- Frequency settings
- Test notification button

Part 4 of 4: Notification system implementation
Closes #500
```

---

## Common Anti-Patterns

### What NOT to Do

**Too vague:**
```
# Bad
fix: bug fix
feat: update
chore: stuff
```

**Wrong type:**
```
# Bad - this is a bug fix, not a feature
feat: fix login button color

# Good
fix(ui): correct login button hover state
```

**Missing context:**
```
# Bad
fix: null pointer

# Good
fix(users): handle null email in profile update
```

**Too much in one commit:**
```
# Bad
feat: add user auth, fix cart bug, update docs, refactor api

# Good - split into separate commits
feat(auth): add JWT authentication
fix(cart): resolve quantity calculation
docs: update API authentication guide
refactor(api): extract middleware functions
```

**Mixing concerns:**
```
# Bad - formatting + feature
feat: add search and format files

# Good - separate commits
style: format files with prettier
feat: add search functionality
```

**Commit message too long:**
```
# Bad (over 72 chars)
feat(user-authentication-service): implement two-factor authentication using TOTP

# Good
feat(auth): implement TOTP two-factor authentication
```

---

## Quick Reference

```
feat:     New feature                    -> MINOR
fix:      Bug fix                        -> PATCH
docs:     Documentation only             -> -
style:    Formatting (no code change)    -> -
refactor: Code restructuring             -> -
perf:     Performance improvement        -> PATCH
test:     Adding/fixing tests            -> -
build:    Build system/dependencies      -> -
ci:       CI configuration               -> -
chore:    Maintenance                    -> -
revert:   Revert previous commit         -> depends

! or BREAKING CHANGE:                    -> MAJOR
```
