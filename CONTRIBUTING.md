# Contributing to Labs Skills

Thank you for your interest in contributing to the Labs Skills repository! This guide explains how to add new skills or improve existing ones.

## Adding a New Skill

### 1. Choose the Right Category

Skills belong in one of these categories:

| Category | When to Use |
|----------|-------------|
| 01-language-frameworks | Language-specific libraries and frameworks |
| 02-architecture-design | Design patterns and architectural decisions |
| 03-testing | Testing tools and strategies |
| 04-devops-deployment | Infrastructure and deployment |
| 05-data-databases | Data storage, streaming, caching |
| 06-ai-ml | AI/ML, LLM integration |
| 07-security | Security practices |
| 08-documentation | Documentation standards |
| 09-code-quality | Linting, typing, code standards |

### 2. Use the Skill Template

```bash
# Create a new Python skill
make new-skill TYPE=python NAME=my-new-skill CATEGORY=01-language-frameworks/python

# Create a new Go skill
make new-skill TYPE=go NAME=my-new-skill CATEGORY=01-language-frameworks/go

# Create a new Frontend skill
make new-skill TYPE=frontend NAME=my-new-skill CATEGORY=01-language-frameworks/frontend
```

### 3. Required Files

Every skill must have:

```
skill-name/
├── README.md           # Required - Entry point
├── CLAUDE.md           # Required - AI guidance
├── Makefile            # Required - Standard commands
├── docs/
│   ├── concepts.md     # Required - Core concepts
│   └── patterns.md     # Required - Common patterns
├── src/ or cmd/        # Required - Working examples
├── exercises/          # Required - Practice problems
│   └── solutions/      # Required - Exercise solutions
└── tests/              # Required - Test coverage
```

### 4. README.md Structure

```markdown
# Skill Name

Brief description of what this skill teaches.

## Learning Objectives

After completing this skill, you will be able to:
- Objective 1
- Objective 2
- Objective 3

## Prerequisites

- List any skills that should be learned first
- Required tools or setup

## Quick Start

\`\`\`bash
make setup
make examples
\`\`\`

## Examples

### Example 1: Basic Usage
[Description and code]

### Example 2: Intermediate Pattern
[Description and code]

### Example 3: Advanced Usage
[Description and code]

## Exercises

See the [exercises](./exercises/) directory for practice problems.

## Further Reading

- Links to official documentation
- Related skills in this repository
```

### 5. CLAUDE.md Structure

```markdown
# CLAUDE.md - [Skill Name]

Brief context for AI assistants working with this skill.

## Key Concepts

- Concept 1: Brief explanation
- Concept 2: Brief explanation

## Common Commands

\`\`\`bash
make setup      # What this does
make examples   # What this does
make test       # What this does
\`\`\`

## Common Mistakes

1. Mistake description
   - How to fix it

## Code Patterns

### Pattern Name
\`\`\`python
# Example code
\`\`\`

## When Users Ask About...

### "How do I...?"
Answer guidance

## Gotchas

- Non-obvious behavior to watch for
```

### 6. Makefile Requirements

Every skill Makefile must support these targets:

```makefile
.PHONY: setup examples test lint clean

setup:      # Install dependencies
examples:   # Run example code
test:       # Run tests
lint:       # Check code quality
clean:      # Clean build artifacts
```

### 7. Exercise Guidelines

- Include at least 3 exercises of increasing difficulty
- Provide clear problem statements
- Include expected output or behavior
- Put solutions in `exercises/solutions/`
- Solutions should include comments explaining the approach

### 8. Test Requirements

- Test all examples
- Test edge cases
- Test error conditions
- Achieve at least 80% code coverage
- Tests must pass with `make test`

## Improving Existing Skills

### Adding Examples

1. Follow the existing example pattern
2. Add progressive complexity
3. Update README.md
4. Add tests for new examples

### Fixing Bugs

1. Add a failing test first
2. Fix the bug
3. Verify all tests pass
4. Update documentation if behavior changed

### Improving Documentation

1. Keep language clear and concise
2. Include code examples
3. Update both README.md and CLAUDE.md
4. Verify links work

## Code Style

### Python
- Format with Ruff
- Type hints required
- Docstrings for public functions
- Follow PEP 8

### Go
- Format with gofmt
- Comments for exported functions
- Follow Go conventions

### Frontend
- Format with Prettier
- TypeScript strict mode
- Functional components

## Pull Request Checklist

Before submitting:

- [ ] All Makefile targets work (`setup`, `examples`, `test`, `lint`, `clean`)
- [ ] README.md has all required sections
- [ ] CLAUDE.md provides useful AI guidance
- [ ] At least 3 progressive examples
- [ ] At least 3 exercises with solutions
- [ ] Tests pass with `make test`
- [ ] Lint passes with `make lint`
- [ ] Documentation is clear and complete

## Questions?

Open an issue for:
- Clarification on where a skill belongs
- Feedback on skill design
- Suggestions for new skills
