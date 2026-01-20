# CLAUDE.md - Conventional Commits Skill

This skill teaches developers how to write consistent, meaningful commit messages following the Conventional Commits specification. It covers commit types, scopes, breaking changes, and tooling like commitlint and Husky.

## Key Concepts

- **Conventional Commits**: A specification for adding human and machine-readable meaning to commit messages
- **Commit Types**: Categorize changes (feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert)
- **Scopes**: Optional context about what part of the codebase is affected
- **Breaking Changes**: Indicated by `!` after type/scope or `BREAKING CHANGE:` footer
- **commitlint**: Tool to enforce commit message conventions
- **Husky**: Git hooks manager that runs commitlint on commit-msg hook

## Common Commands

```bash
make setup      # Install commitlint, husky, and dependencies
make examples   # Display example commit messages
make test       # Test commitlint configuration with valid/invalid messages
make lint       # Validate commit message format
make clean      # Remove node_modules and build artifacts
```

## Project Structure

```
commit-standards/
├── README.md                 # Skill overview and quick start
├── CLAUDE.md                 # This file - AI guidance
├── package.json              # Node dependencies (commitlint, husky)
├── Makefile                  # Standard commands
├── commitlint.config.js      # commitlint configuration
├── .husky/
│   └── commit-msg            # Git hook for validation
├── docs/
│   ├── concepts.md           # Deep dive on conventions
│   └── patterns.md           # Real-world commit examples
├── examples/
│   ├── 01-basic-commits/     # Simple commit types
│   ├── 02-scoped-commits/    # Scopes and bodies
│   └── 03-breaking-changes/  # Breaking change patterns
├── exercises/
│   ├── exercise-1.md         # Categorize and write commits
│   ├── exercise-2.md         # Fix bad commit messages
│   ├── exercise-3.md         # Feature implementation commits
│   └── solutions/
└── src/
    └── validate-commit.js    # Utility to validate messages
```

## Commit Message Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Valid Types
- `feat` - New feature (triggers MINOR version bump)
- `fix` - Bug fix (triggers PATCH version bump)
- `docs` - Documentation changes only
- `style` - Code style (formatting, semicolons, etc.)
- `refactor` - Code change that neither fixes bug nor adds feature
- `perf` - Performance improvement
- `test` - Adding or correcting tests
- `build` - Build system or external dependencies
- `ci` - CI/CD configuration
- `chore` - Other changes that don't modify src or test
- `revert` - Reverts a previous commit

## Code Patterns

### Pattern 1: Basic Commit
```
feat: add user registration endpoint
```

### Pattern 2: Scoped Commit
```
fix(auth): resolve token expiration check
```

### Pattern 3: Commit with Body
```
refactor(api): simplify request validation

Extract common validation logic into middleware.
Remove duplicate checks from individual handlers.
```

### Pattern 4: Breaking Change with Footer
```
feat(api): change response format to JSON:API

BREAKING CHANGE: All API responses now follow JSON:API spec.
Clients must update parsers to handle new structure.
```

### Pattern 5: Breaking Change with `!`
```
feat(api)!: change response format to JSON:API

All API responses now follow JSON:API spec.
```

## Common Mistakes

1. **Capitalizing the description**
   - Wrong: `feat: Add new feature`
   - Correct: `feat: add new feature`
   - Reason: Conventional commits uses lowercase by convention

2. **Using wrong type**
   - Wrong: `feat: fix typo in documentation`
   - Correct: `docs: fix typo in API documentation`
   - Reason: Documentation changes are `docs`, not `feat`

3. **Missing type**
   - Wrong: `fixed the login bug`
   - Correct: `fix(auth): resolve login redirect loop`
   - Reason: Type is required for conventional commits

4. **Vague descriptions**
   - Wrong: `fix: bug fix`
   - Correct: `fix(cart): prevent negative quantity values`
   - Reason: Description should explain what changed

5. **Not marking breaking changes**
   - Wrong: `refactor: change API return type`
   - Correct: `refactor!: change API return type` or use BREAKING CHANGE footer
   - Reason: Breaking changes must be clearly indicated

## When Users Ask About...

### "What commit type should I use?"
Guide them through decision tree:
1. New functionality? -> `feat`
2. Bug fix? -> `fix`
3. Documentation? -> `docs`
4. Formatting/linting? -> `style`
5. Restructuring code? -> `refactor`
6. Performance? -> `perf`
7. Tests? -> `test`
8. Build/deps? -> `build`
9. CI/CD? -> `ci`
10. Everything else? -> `chore`

### "How do I indicate breaking changes?"
Two options:
1. Add `!` after type/scope: `feat(api)!: change auth flow`
2. Add `BREAKING CHANGE:` footer in commit body

### "Should I use scopes?"
Scopes are optional but recommended for:
- Large codebases with distinct modules
- Monorepos with multiple packages
- When multiple teams work on same repo
Common scopes: `api`, `ui`, `auth`, `db`, `config`, `deps`

### "How long should commit messages be?"
- Header (first line): Max 72 characters
- Body: Wrap at 72-100 characters per line
- Be concise but descriptive

### "How do I set up commitlint?"
Point them to the setup:
```bash
npm install --save-dev @commitlint/cli @commitlint/config-conventional
# Add commitlint.config.js
# Set up husky hooks
```

## Tooling Notes

### commitlint
- Validates commit messages against conventional commits spec
- Configuration in `commitlint.config.js`
- Can customize rules (types, scopes, max length, etc.)

### Husky
- Manages Git hooks
- `commit-msg` hook runs commitlint
- Prevents bad commits from being created

### Semantic Release Integration
- Conventional commits enable automated releases
- `fix` -> patch version
- `feat` -> minor version
- `BREAKING CHANGE` -> major version

## Testing Notes

- Test valid commits pass commitlint
- Test invalid commits fail with helpful errors
- Test custom rules are enforced
- Run `make test` to verify configuration

## Dependencies

Key dependencies in package.json:
- `@commitlint/cli`: CLI for commitlint
- `@commitlint/config-conventional`: Shareable config for conventional commits
- `husky`: Git hooks manager
