# Example 3: Breaking Changes

This example covers how to properly indicate and document breaking changes in your commits.

## Learning Goals

- Understand what constitutes a breaking change
- Learn the two methods for indicating breaking changes
- Write comprehensive breaking change documentation
- Understand the connection to semantic versioning

## What is a Breaking Change?

A breaking change is any modification that requires consumers of your code to update their implementations:

- Removing public APIs or functions
- Changing function signatures (parameters, return types)
- Modifying response formats or data structures
- Changing default behavior
- Removing configuration options
- Renaming exported symbols

## Indicating Breaking Changes

### Method 1: The `!` Notation

Add `!` immediately after the type (and scope if present):

```
feat!: remove deprecated user endpoints
feat(api)!: change authentication flow
fix(db)!: require explicit connection string
```

### Method 2: The `BREAKING CHANGE` Footer

Add a `BREAKING CHANGE:` footer in the commit body:

```
refactor(api): change response format

BREAKING CHANGE: All API responses now use JSON:API format.
Existing clients must update their parsers.
```

### Method 3: Both (Recommended for Major Changes)

For maximum visibility, use both methods:

```
feat(api)!: replace REST with GraphQL

Migrated all endpoints to GraphQL API.

BREAKING CHANGE: REST endpoints have been removed.
Use GraphQL queries and mutations instead.
See migration guide: docs/graphql-migration.md
```

## Real-World Examples

### API Response Change

```
feat(api)!: change pagination to cursor-based

BREAKING CHANGE: Pagination parameters have changed.

Before:
  GET /users?page=2&per_page=20

After:
  GET /users?cursor=abc123&limit=20

Response format also changed:
  Before: { data: [], page: 2, total_pages: 10 }
  After:  { data: [], next_cursor: "xyz789", has_more: true }

Migration: Replace page/per_page with cursor/limit.
Store next_cursor from responses for subsequent requests.
```

### Configuration Change

```
feat(config)!: require explicit environment setting

BREAKING CHANGE: NODE_ENV must now be explicitly set.

Previously defaulted to 'development' which caused issues
in production deployments where it wasn't set.

Action required:
1. Add NODE_ENV=production to production .env
2. Add NODE_ENV=development to development .env
3. Add NODE_ENV=test to test configuration
```

### Function Signature Change

```
refactor(auth)!: change authenticate function signature

BREAKING CHANGE: authenticate() now requires options object.

Before:
  authenticate(username, password, rememberMe)

After:
  authenticate({ username, password, options: { rememberMe } })

Migration:
  // Old
  authenticate('user', 'pass', true)

  // New
  authenticate({
    username: 'user',
    password: 'pass',
    options: { rememberMe: true }
  })
```

### Dependency Removal

```
build(deps)!: remove lodash dependency

BREAKING CHANGE: lodash is no longer included.

If your code imports lodash through this package,
you must now install it directly:

  npm install lodash

Affected utilities:
- _.debounce -> Use native or install separately
- _.throttle -> Use native or install separately
- _.merge -> Use native Object spread or structuredClone
```

## Demo Script

Run the demo to see these examples validated:

```bash
npm run example:3
# or
make example-3
```

## Semantic Versioning Impact

Breaking changes trigger MAJOR version bumps:

| Current Version | After Breaking Change |
|-----------------|----------------------|
| 1.2.3 | 2.0.0 |
| 0.5.2 | 1.0.0 |
| 2.0.0 | 3.0.0 |

This is why proper breaking change notation is crucial - it affects how your package is versioned automatically.

## Documentation Checklist

When documenting a breaking change, include:

- [ ] **What changed**: Describe the modification
- [ ] **Why it changed**: Explain the reasoning
- [ ] **Before/After**: Show concrete examples
- [ ] **Migration steps**: Guide users to update
- [ ] **Timeline**: When was it deprecated (if applicable)

## Practice

Write breaking change commits for these scenarios:

1. Removing the deprecated `/api/v1/users` endpoint
2. Changing the default timeout from 30s to 10s
3. Requiring Node.js 18+ (dropping Node 16 support)

<details>
<summary>Click to see example solutions</summary>

1. ```
   feat(api)!: remove deprecated v1 users endpoint

   BREAKING CHANGE: /api/v1/users has been removed.

   This endpoint was deprecated in v2.0.0 (March 2023).
   Use /api/v2/users instead.

   Migration:
     Before: GET /api/v1/users
     After:  GET /api/v2/users

   Response format is compatible - no other changes needed.
   ```

2. ```
   feat(config)!: reduce default timeout to 10 seconds

   BREAKING CHANGE: Default request timeout changed from 30s to 10s.

   This improves failure detection and prevents hung requests.
   If you need longer timeouts, explicitly configure them:

     const client = new Client({ timeout: 30000 });

   Or set via environment variable:
     REQUEST_TIMEOUT=30000
   ```

3. ```
   build!: require Node.js 18 or higher

   BREAKING CHANGE: Node.js 16 is no longer supported.

   Node 16 reached end-of-life on September 11, 2023.
   This update enables:
   - Native fetch API
   - Improved performance
   - Better security updates

   Action required: Upgrade to Node.js 18 LTS or 20 LTS.
   ```

</details>

## Common Mistakes

### Mistake 1: Not Marking Breaking Changes

```
# Wrong - this IS a breaking change but not marked
refactor(api): change response format

# Correct
refactor(api)!: change response format
```

### Mistake 2: Missing Migration Guide

```
# Incomplete
feat!: remove old API

BREAKING CHANGE: Old API removed.

# Better
feat!: remove old API

BREAKING CHANGE: Old API removed.

Migration steps:
1. Update imports from 'old-api' to 'new-api'
2. Replace oldMethod() with newMethod()
3. See docs/migration.md for full guide
```

### Mistake 3: Not Documenting Timeline

```
# Missing context
feat(api)!: remove deprecated endpoint

# Better - shows deprecation timeline
feat(api)!: remove deprecated endpoint

BREAKING CHANGE: /legacy endpoint removed.

Deprecated: v2.0.0 (January 2023)
Removal: v3.0.0 (this release)

Users had 6 months to migrate to /v2 endpoint.
```

## Key Takeaways

1. **Breaking changes must be marked**: Use `!` or `BREAKING CHANGE` footer
2. **Be thorough**: Document what changed, why, and how to migrate
3. **Show before/after**: Concrete examples help users migrate
4. **Major version = breaking changes**: This affects semantic versioning
5. **Consider deprecation first**: Give users time to migrate when possible

## Next Steps

Practice what you've learned in the [Exercises](../../exercises/) section.
