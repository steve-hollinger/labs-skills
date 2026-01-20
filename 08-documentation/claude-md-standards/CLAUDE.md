# CLAUDE.md - CLAUDE.md Standards Skill

This skill teaches developers how to write effective CLAUDE.md files that provide AI assistants with proper context and guidance for working in codebases.

## Key Concepts

- **Context Setting**: CLAUDE.md provides project-specific context that helps AI understand your codebase
- **Actionable Guidance**: Good CLAUDE.md files contain specific, actionable instructions
- **Hierarchy Support**: CLAUDE.md files can be nested, with more specific files taking precedence
- **Maintenance**: CLAUDE.md files must be kept current to remain useful

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run basic structure example
make example-2  # Run good vs bad guidance example
make example-3  # Run project templates example
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
claude-md-standards/
├── src/claude_md_standards/
│   ├── __init__.py
│   └── examples/
│       ├── __init__.py
│       ├── example_1.py      # Basic CLAUDE.md structure
│       ├── example_2.py      # Good vs bad guidance
│       └── example_3.py      # Project templates
├── exercises/
│   ├── exercise_1.py         # Flask API CLAUDE.md
│   ├── exercise_2.py         # Improve bad CLAUDE.md
│   ├── exercise_3.py         # Monorepo hierarchy
│   └── solutions/
├── tests/
│   └── test_examples.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Section-Based Structure
```python
STANDARD_SECTIONS = [
    "Purpose/Overview",
    "Key Commands",
    "Architecture Decisions",
    "Code Patterns",
    "Common Mistakes",
    "When Users Ask About..."
]
```

### Pattern 2: Validation Approach
```python
def validate_claude_md(content: str) -> ValidationResult:
    """Check CLAUDE.md for required sections and quality."""
    # Check for essential sections
    # Verify actionable content
    # Flag vague language
```

## Common Mistakes

1. **Writing for humans, not AI**
   - CLAUDE.md should be optimized for AI parsing
   - Use clear headers and consistent formatting

2. **Including implementation details that change frequently**
   - Focus on stable patterns and decisions
   - Avoid version numbers or specific file paths that change often

3. **Forgetting the "why" behind decisions**
   - AI needs context to make good suggestions
   - Explain reasoning, not just rules

## When Users Ask About...

### "What sections should my CLAUDE.md have?"
Point them to Example 1 which shows the standard structure. Key sections are:
- Overview/Purpose
- Key Commands
- Architecture Decisions
- Code Patterns
- Common Mistakes

### "How long should CLAUDE.md be?"
Aim for 100-300 lines. Long enough to be comprehensive, short enough to be digestible.

### "How do I know if my CLAUDE.md is good?"
Run the validation in Example 2. Check that:
- Every section has actionable content
- Commands are tested and work
- Language is specific, not vague

### "Should I have multiple CLAUDE.md files?"
Yes, for larger projects. Root CLAUDE.md covers general guidance, subdirectory files provide specific context.

## Testing Notes

- Tests validate CLAUDE.md parsing and generation
- Example outputs are verified against templates
- Run `make test` to ensure examples work correctly

## Dependencies

Key dependencies in pyproject.toml:
- pydantic: Data validation for CLAUDE.md structure
- jinja2: Template rendering for project-type examples
- rich: Terminal output formatting
