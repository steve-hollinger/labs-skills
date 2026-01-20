# Conventional Commits

A comprehensive skill for mastering conventional commit message standards, the specification that provides a lightweight convention for creating an explicit commit history.

## Learning Objectives

After completing this skill, you will be able to:
- Understand and apply the Conventional Commits specification
- Write clear, consistent commit messages using proper types (feat, fix, docs, etc.)
- Use scopes to provide additional contextual information
- Indicate breaking changes appropriately
- Configure commitlint to enforce commit standards
- Set up Husky git hooks for automated validation
- Integrate commit standards into CI/CD pipelines

## Prerequisites

- Git basics (staging, committing, pushing)
- Node.js 18+ (for commitlint and husky)
- npm or yarn package manager
- Basic command-line familiarity

## Quick Start

```bash
# Install dependencies
make setup

# Run examples
make examples

# Test commitlint configuration
make test

# Validate a commit message
make lint

# Clean build artifacts
make clean
```

## Concepts

### What is Conventional Commits?

Conventional Commits is a specification for adding human and machine-readable meaning to commit messages. It provides a set of rules for creating an explicit commit history, which makes it easier to write automated tools on top of.

### The Commit Message Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Commit Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat: add user authentication` |
| `fix` | Bug fix | `fix: resolve null pointer in user service` |
| `docs` | Documentation only | `docs: update API documentation` |
| `style` | Formatting, no code change | `style: format with prettier` |
| `refactor` | Code change without fix/feature | `refactor: extract validation logic` |
| `perf` | Performance improvement | `perf: optimize database queries` |
| `test` | Adding or correcting tests | `test: add unit tests for auth module` |
| `build` | Build system or dependencies | `build: upgrade webpack to v5` |
| `ci` | CI configuration | `ci: add GitHub Actions workflow` |
| `chore` | Other maintenance | `chore: update .gitignore` |
| `revert` | Revert previous commit | `revert: revert feat(auth): add login` |

### Why Use Conventional Commits?

1. **Automated Changelog Generation**: Tools can automatically generate CHANGELOG.md
2. **Semantic Versioning**: Determine version bumps automatically (major, minor, patch)
3. **Clear Communication**: Team members understand changes at a glance
4. **Better Git History**: Structured commits make history easier to navigate
5. **Tooling Integration**: Works with semantic-release, standard-version, etc.

## Examples

### Example 1: Basic Commits

Learn the fundamental commit types and how to write simple, effective commit messages.

```bash
make example-1
```

See [examples/01-basic-commits/](./examples/01-basic-commits/) for detailed walkthroughs.

### Example 2: Scoped Commits

Add context with scopes and write more detailed commit messages with bodies and footers.

```bash
make example-2
```

See [examples/02-scoped-commits/](./examples/02-scoped-commits/) for detailed walkthroughs.

### Example 3: Breaking Changes

Handle breaking changes properly with BREAKING CHANGE footers and the `!` notation.

```bash
make example-3
```

See [examples/03-breaking-changes/](./examples/03-breaking-changes/) for detailed walkthroughs.

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Categorize changes and write appropriate commit messages
2. **Exercise 2**: Fix poorly-written commit messages using conventional format
3. **Exercise 3**: Write a series of commits for a feature implementation

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Tools Setup

### commitlint Configuration

This skill includes a pre-configured `commitlint.config.js`:

```javascript
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [2, 'always', [
      'feat', 'fix', 'docs', 'style', 'refactor',
      'perf', 'test', 'build', 'ci', 'chore', 'revert'
    ]],
    'subject-case': [2, 'always', 'lower-case'],
    'header-max-length': [2, 'always', 72]
  }
};
```

### Husky Git Hooks

The `.husky/` directory contains pre-configured git hooks:

```bash
# .husky/commit-msg
npx --no -- commitlint --edit $1
```

## Common Mistakes

### Mistake 1: Vague Descriptions

**Bad**: `fix: bug fix`
**Good**: `fix: resolve race condition in user session handler`

### Mistake 2: Wrong Commit Type

**Bad**: `feat: fix typo in readme` (this is not a feature)
**Good**: `docs: fix typo in readme`

### Mistake 3: Missing Breaking Change Notation

**Bad**: `refactor: change API response format` (breaks existing clients)
**Good**: `refactor!: change API response format`

Or with footer:
```
refactor: change API response format

BREAKING CHANGE: Response now returns array instead of object
```

### Mistake 4: Scope Too Broad or Missing

**Bad**: `fix: button color`
**Good**: `fix(ui): correct primary button hover color`

### Mistake 5: Description Starts with Capital

**Bad**: `feat: Add new feature`
**Good**: `feat: add new feature`

## Semantic Versioning Integration

Conventional Commits maps directly to semantic versioning:

| Commit Type | Version Bump | Example |
|-------------|--------------|---------|
| `fix:` | PATCH (0.0.x) | 1.0.0 -> 1.0.1 |
| `feat:` | MINOR (0.x.0) | 1.0.0 -> 1.1.0 |
| `BREAKING CHANGE` | MAJOR (x.0.0) | 1.0.0 -> 2.0.0 |

## Further Reading

- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [commitlint Documentation](https://commitlint.js.org/)
- [Husky Documentation](https://typicode.github.io/husky/)
- [Semantic Versioning](https://semver.org/)
- Related skills in this repository:
  - [golangci-lint](../go/golangci-lint/)
  - [Ruff Python Linting](../python/ruff-linting/)
