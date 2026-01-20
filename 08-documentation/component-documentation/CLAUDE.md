# CLAUDE.md - Component Documentation Skill

This skill teaches developers how to document software components including README files, API documentation, and inline code documentation.

## Key Concepts

- **README Structure**: Standard sections every README needs
- **API Documentation**: Documenting endpoints, parameters, responses, and errors
- **Code Documentation**: Docstrings, type hints, and inline comments
- **Documentation Maintenance**: Keeping docs in sync with code

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # README structure example
make example-2  # API documentation example
make example-3  # Code documentation example
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
component-documentation/
├── src/component_documentation/
│   ├── __init__.py
│   ├── models.py         # Documentation data models
│   ├── readme_builder.py # README generation utilities
│   ├── api_docs.py       # API documentation utilities
│   ├── code_docs.py      # Code documentation analysis
│   └── examples/
│       ├── example_1.py  # README structure
│       ├── example_2.py  # API documentation
│       └── example_3.py  # Code documentation
├── exercises/
│   ├── exercise_1.py     # README for existing code
│   ├── exercise_2.py     # API documentation
│   ├── exercise_3.py     # Document undocumented code
│   └── solutions/
├── tests/
│   └── test_examples.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: README Sections
```python
README_SECTIONS = [
    "Title & Description",
    "Installation",
    "Quick Start",
    "Usage Examples",
    "API Reference",
    "Configuration",
    "Contributing",
    "License",
]
```

### Pattern 2: Docstring Style
```python
def process_data(items: list[dict], limit: int = 100) -> ProcessResult:
    """Process a list of data items.

    Args:
        items: List of dictionaries containing item data.
        limit: Maximum number of items to process.

    Returns:
        ProcessResult containing processed items and metadata.

    Raises:
        ValidationError: If items contain invalid data.
        ProcessingError: If processing fails.

    Example:
        >>> result = process_data([{"id": 1, "value": "test"}])
        >>> print(result.count)
        1
    """
```

## Common Mistakes

1. **Writing documentation after the fact**
   - Write README first (README-driven development)
   - Update docs as part of the PR

2. **Generic descriptions without examples**
   - Show working code, not just explanations
   - Include error cases, not just happy paths

3. **Assuming reader context**
   - Explain what things are, not just how to use them
   - Define terms and abbreviations

## When Users Ask About...

### "What should go in a README?"
Minimum: title, description, installation, quick start, examples.
Better: also configuration, API reference, contributing, license.

### "How detailed should docstrings be?"
Public APIs need full docstrings with args, returns, raises, and examples.
Private functions can be shorter but still explain the "why".

### "Should I document everything?"
Document public APIs thoroughly. For internal code, focus on non-obvious logic.

### "How do I keep docs updated?"
Include documentation review in PR checklist. Use CI to check for missing docs.

## Testing Notes

- Tests validate documentation structure and quality
- Example outputs are verified for completeness
- Run `make test` to ensure examples work

## Dependencies

Key dependencies in pyproject.toml:
- pydantic: Data models for documentation
- rich: Terminal formatting
