# Conventional Commits: Core Concepts

This document provides a deep dive into the Conventional Commits specification, explaining the reasoning behind each element and how to apply them effectively.

## Table of Contents

1. [What is Conventional Commits?](#what-is-conventional-commits)
2. [The Anatomy of a Commit Message](#the-anatomy-of-a-commit-message)
3. [Commit Types Explained](#commit-types-explained)
4. [Understanding Scopes](#understanding-scopes)
5. [Breaking Changes](#breaking-changes)
6. [Footers and Metadata](#footers-and-metadata)
7. [Semantic Versioning Connection](#semantic-versioning-connection)
8. [Tooling Ecosystem](#tooling-ecosystem)

---

## What is Conventional Commits?

Conventional Commits is a lightweight specification for writing standardized commit messages. It provides a set of rules that make commits:

- **Human-readable**: Anyone can understand what changed at a glance
- **Machine-parseable**: Tools can automatically generate changelogs and determine version bumps
- **Consistent**: Every commit follows the same format

### The Specification

The specification is maintained at [conventionalcommits.org](https://www.conventionalcommits.org/) and is designed to work alongside [Semantic Versioning (SemVer)](https://semver.org/).

### Why It Matters

Without a standard format, commit messages become inconsistent:

```
# These are all describing the same type of change
Fixed bug in login
Login fix
fix login issue
Resolve authentication problem
bugfix: auth
```

With Conventional Commits, they all become:

```
fix(auth): resolve login redirect loop
```

---

## The Anatomy of a Commit Message

A conventional commit message has three parts:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Part 1: The Header

The header is the first line and must follow this format:

```
<type>[optional scope]: <description>
```

**Rules:**
- Must be 72 characters or less
- Type is required
- Scope is optional (in parentheses)
- Colon and space after type/scope
- Description is required
- Description should be lowercase
- No period at the end

**Examples:**
```
feat: add user registration endpoint
fix(auth): resolve token expiration issue
docs(api): update authentication documentation
```

### Part 2: The Body

The body provides additional context about the change:

```
fix(auth): resolve token expiration issue

The JWT token was being validated against the creation time
instead of the expiration time. This caused valid tokens to
be rejected after server restart.

Updated the validation logic to use the 'exp' claim correctly.
```

**Rules:**
- Must be separated from header by a blank line
- Can be multiple paragraphs
- Should explain the "why" not just the "what"
- Each line should be 100 characters or less

### Part 3: The Footer

Footers contain metadata like breaking changes or issue references:

```
feat(api): add pagination to list endpoints

Added offset and limit parameters to all list endpoints.
Default page size is 20 items.

BREAKING CHANGE: List endpoints no longer return all items by default.
Clients must handle pagination or explicitly request all items.

Closes #123
Refs #456, #789
```

**Common Footer Formats:**
- `BREAKING CHANGE: <description>`
- `Closes #<issue>`
- `Fixes #<issue>`
- `Refs #<issue>`
- `Reviewed-by: <name>`
- `Co-authored-by: <name> <email>`

---

## Commit Types Explained

Each type has a specific meaning. Using the correct type is crucial for automated tooling.

### `feat` - New Features

Use when adding new functionality that users/consumers can interact with.

```
feat: add dark mode toggle
feat(ui): implement responsive navigation
feat(api): add webhook support for order events
```

**Triggers:** MINOR version bump (e.g., 1.0.0 -> 1.1.0)

### `fix` - Bug Fixes

Use when fixing something that was broken.

```
fix: resolve null pointer in user lookup
fix(cart): prevent negative quantities
fix(auth): handle expired refresh tokens correctly
```

**Triggers:** PATCH version bump (e.g., 1.0.0 -> 1.0.1)

### `docs` - Documentation

Use for documentation-only changes.

```
docs: update installation instructions
docs(api): add authentication examples
docs(readme): fix broken links
```

**Triggers:** No version bump

### `style` - Code Style

Use for formatting changes that don't affect code behavior.

```
style: format code with prettier
style(api): fix indentation in routes
style: remove trailing whitespace
```

**Note:** This is NOT for CSS styling changes (those are `feat` or `fix`).

**Triggers:** No version bump

### `refactor` - Code Refactoring

Use when restructuring code without changing behavior.

```
refactor: extract validation into separate module
refactor(auth): simplify token generation logic
refactor(db): migrate from callbacks to async/await
```

**Triggers:** No version bump

### `perf` - Performance

Use for performance improvements.

```
perf: optimize image loading with lazy load
perf(db): add index for user lookups
perf(api): implement response caching
```

**Triggers:** PATCH version bump (varies by project)

### `test` - Tests

Use when adding or fixing tests.

```
test: add unit tests for user service
test(auth): increase coverage for edge cases
test(e2e): fix flaky login test
```

**Triggers:** No version bump

### `build` - Build System

Use for changes to build process or dependencies.

```
build: upgrade webpack to v5
build(deps): update lodash to fix vulnerability
build: add docker multi-stage build
```

**Triggers:** No version bump (unless deps affect public API)

### `ci` - Continuous Integration

Use for CI/CD configuration changes.

```
ci: add GitHub Actions workflow
ci: configure automated release
ci(deploy): add staging environment
```

**Triggers:** No version bump

### `chore` - Maintenance

Use for other maintenance tasks.

```
chore: update .gitignore
chore: clean up unused files
chore(release): bump version to 2.0.0
```

**Triggers:** No version bump

### `revert` - Reverting

Use when reverting a previous commit.

```
revert: revert "feat(api): add pagination"

This reverts commit abc123def456.
```

**Triggers:** Depends on what was reverted

---

## Understanding Scopes

Scopes provide context about which part of the codebase is affected.

### When to Use Scopes

Scopes are optional but recommended when:
- Working in a monorepo with multiple packages
- Codebase has distinct modules or domains
- Multiple teams work on the same repository
- You want more granular changelogs

### Common Scope Patterns

**By Module:**
```
feat(auth): add two-factor authentication
fix(payments): handle currency conversion
```

**By Package (Monorepo):**
```
feat(@company/ui): add button component
fix(@company/api): resolve rate limiting issue
```

**By Layer:**
```
fix(api): validate request headers
refactor(db): optimize query performance
```

**By Feature:**
```
feat(checkout): add express checkout
fix(search): improve relevance scoring
```

### Scope Best Practices

1. **Keep scopes consistent**: Define allowed scopes in commitlint config
2. **Use lowercase**: `auth` not `Auth`
3. **Keep it short**: `ui` not `user-interface`
4. **Be specific enough**: `api-auth` vs just `api` if needed

---

## Breaking Changes

Breaking changes require special handling because they affect consumers of your code.

### What is a Breaking Change?

A breaking change is any modification that requires consumers to update their code:

- Removing or renaming public APIs
- Changing function signatures
- Modifying return types or response formats
- Removing configuration options
- Changing default behavior

### Indicating Breaking Changes

**Method 1: Using `!` notation**

Add `!` after the type/scope:

```
feat(api)!: change authentication flow

The /login endpoint now requires OAuth2 tokens instead of API keys.
```

**Method 2: Using `BREAKING CHANGE` footer**

Add a `BREAKING CHANGE:` footer:

```
refactor(api): change response format

BREAKING CHANGE: All API responses now use JSON:API format.
Existing clients must update their parsers.
```

**Method 3: Both**

For maximum clarity, use both:

```
feat(api)!: replace REST with GraphQL

Migrated all endpoints to GraphQL API.

BREAKING CHANGE: REST endpoints are removed. Use GraphQL queries
and mutations instead. See migration guide at docs/migration.md.
```

### Breaking Changes Trigger Major Version

Any commit with a breaking change triggers a MAJOR version bump:

- `1.2.3` -> `2.0.0`
- `0.9.5` -> `1.0.0`

---

## Footers and Metadata

Footers provide additional metadata and references.

### Issue References

```
feat(auth): add password reset flow

Implemented password reset with email verification.

Fixes #234
Closes #235
Refs #100
```

- `Fixes`/`Closes`: Automatically closes the issue
- `Refs`: References without closing

### Co-authors

```
feat: implement search functionality

Co-authored-by: Jane Doe <jane@example.com>
Co-authored-by: John Smith <john@example.com>
```

### Review Information

```
fix(security): patch XSS vulnerability

Reviewed-by: Security Team <security@company.com>
Signed-off-by: Developer <dev@company.com>
```

---

## Semantic Versioning Connection

Conventional Commits maps directly to Semantic Versioning:

| Commit Type | Version Part | Example |
|-------------|--------------|---------|
| `fix:` | PATCH | 1.0.0 -> 1.0.1 |
| `feat:` | MINOR | 1.0.0 -> 1.1.0 |
| `BREAKING CHANGE` | MAJOR | 1.0.0 -> 2.0.0 |

### Version Bump Decision Tree

```
Is there a BREAKING CHANGE?
├── Yes -> MAJOR bump
└── No -> Is there a feat?
          ├── Yes -> MINOR bump
          └── No -> Is there a fix?
                    ├── Yes -> PATCH bump
                    └── No -> No bump
```

### Pre-1.0 Behavior

For versions < 1.0.0, some projects treat:
- `feat:` as PATCH (0.0.x)
- Breaking changes as MINOR (0.x.0)

---

## Tooling Ecosystem

### Validation: commitlint

```bash
# Install
npm install --save-dev @commitlint/cli @commitlint/config-conventional

# Use
echo "feat: add feature" | commitlint
```

### Git Hooks: Husky

```bash
# Install
npm install --save-dev husky

# Initialize
npx husky init

# Add commit-msg hook
echo 'npx --no -- commitlint --edit $1' > .husky/commit-msg
```

### Release Automation: semantic-release

```bash
# Install
npm install --save-dev semantic-release

# Configure in package.json
{
  "release": {
    "branches": ["main"]
  }
}
```

### Changelog Generation: conventional-changelog

```bash
# Install
npm install --save-dev conventional-changelog-cli

# Generate
npx conventional-changelog -p angular -i CHANGELOG.md -s
```

### Interactive Commits: commitizen

```bash
# Install
npm install --save-dev commitizen cz-conventional-changelog

# Use
npx cz
```

---

## Summary

Conventional Commits provides:

1. **Structure**: Consistent format for all commits
2. **Semantics**: Clear meaning through types and scopes
3. **Automation**: Enable tooling for releases and changelogs
4. **Communication**: Better team collaboration through clear history

Start simple with just types and descriptions, then add scopes and footers as your project grows.
