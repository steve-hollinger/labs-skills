# Core Concepts

## Overview

CLAUDE.md files serve as AI-specific documentation that helps AI assistants understand your project context, conventions, and constraints. This guide covers the essential concepts for writing effective CLAUDE.md files.

## Concept 1: Purpose of CLAUDE.md

### What It Is

CLAUDE.md is a Markdown file that provides structured context and guidance specifically for AI assistants. Unlike README.md (which targets human developers), CLAUDE.md is optimized for AI consumption.

### Why It Matters

AI assistants process your codebase without the institutional knowledge that human team members accumulate over time. CLAUDE.md bridges this gap by explicitly documenting:
- Project-specific conventions
- Architectural decisions and their rationale
- Common pitfalls and how to avoid them
- Preferred patterns and anti-patterns

### How It Works

When an AI assistant starts working on your project, it reads CLAUDE.md to understand:

```python
# What AI learns from CLAUDE.md
context = {
    "project_purpose": "What does this project do?",
    "key_commands": "How do I build/test/run this?",
    "architecture": "What patterns should I follow?",
    "constraints": "What should I avoid doing?",
    "conventions": "What style should I use?"
}
```

## Concept 2: The CLAUDE.md Hierarchy

### What It Is

CLAUDE.md files can exist at multiple levels in your project structure. When nested, more specific files augment (and can override) more general ones.

### Why It Matters

Large projects have different contexts for different areas. A monorepo might have:
- Root-level guidance for overall conventions
- Service-specific guidance for each microservice
- Module-specific guidance for complex subsystems

### How It Works

```
my-project/
├── CLAUDE.md                    # Root: general project context
├── services/
│   ├── CLAUDE.md                # Services: shared patterns
│   ├── user-service/
│   │   └── CLAUDE.md            # User service specific
│   └── payment-service/
│       └── CLAUDE.md            # Payment service specific
└── shared/
    └── CLAUDE.md                # Shared libraries context
```

Context merging:
```python
def resolve_context(file_path: str) -> dict:
    """
    AI reads CLAUDE.md files from root to current directory,
    merging context with more specific files taking precedence.
    """
    contexts = []
    for level in path_to_root(file_path):
        if exists(f"{level}/CLAUDE.md"):
            contexts.append(parse(f"{level}/CLAUDE.md"))
    return merge_contexts(contexts)  # Later contexts override earlier
```

## Concept 3: Actionable vs. Aspirational Content

### What It Is

Actionable content tells AI exactly what to do. Aspirational content describes ideals without providing specific guidance.

### Why It Matters

AI assistants work best with concrete instructions. Vague guidance leads to inconsistent results or the AI asking for clarification.

### How It Works

**Aspirational (Avoid):**
```markdown
## Code Style
Follow best practices and write clean code.
```

**Actionable (Preferred):**
```markdown
## Code Style
- Use snake_case for functions and variables
- Use PascalCase for classes
- Maximum line length: 100 characters
- Always include type hints on function signatures
- Use docstrings for public functions (Google style)

Example:
    def calculate_total(items: list[Item], tax_rate: float = 0.08) -> Decimal:
        \"\"\"Calculate the total price including tax.

        Args:
            items: List of items to total.
            tax_rate: Tax rate as decimal (default 8%).

        Returns:
            Total price with tax applied.
        \"\"\"
```

## Concept 4: Command Documentation

### What It Is

A section that documents the exact commands needed to work with your project.

### Why It Matters

AI assistants frequently need to run commands (build, test, lint). Without accurate command documentation, AI might:
- Use incorrect commands that fail
- Miss important flags or options
- Not know how to verify their changes

### How It Works

```markdown
## Key Commands

```bash
# Development
make setup          # Install all dependencies
make dev            # Start development server
make test           # Run all tests
make test-unit      # Run only unit tests
make lint           # Check code style
make format         # Auto-fix code style

# Database
make db-migrate     # Run pending migrations
make db-seed        # Populate test data
make db-reset       # Drop and recreate database

# Deployment
make build          # Build production artifacts
make deploy-staging # Deploy to staging environment
```

**Note:** Always run `make lint` before committing.
```

## Concept 5: Pattern Documentation

### What It Is

Documentation of the patterns and conventions used in your codebase, with concrete examples.

### Why It Matters

Every codebase develops its own patterns. Documenting these ensures AI suggestions fit your existing architecture.

### How It Works

```markdown
## Code Patterns

### Error Handling
We use custom exception classes with context:

```python
# Good
raise UserNotFoundError(user_id=user_id, searched_by="email")

# Bad - generic exception
raise Exception("User not found")

# Bad - missing context
raise UserNotFoundError()
```

### Repository Pattern
All database access goes through repository classes:

```python
# Good - using repository
user = await user_repository.get_by_id(user_id)

# Bad - direct database access
user = await db.execute("SELECT * FROM users WHERE id = ?", user_id)
```
```

## Summary

Key takeaways:
1. **CLAUDE.md is for AI** - Optimize content for AI consumption, not human reading
2. **Hierarchy enables specificity** - Use nested files for context-appropriate guidance
3. **Be actionable** - Provide concrete instructions with examples, not vague guidelines
4. **Document commands** - List exact commands that AI can copy and run
5. **Show patterns** - Include code examples of right and wrong approaches
