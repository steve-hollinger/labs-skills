# CLAUDE.md - System Prompts Skill

This skill teaches prompt engineering for system prompts, focusing on the four-component structure (role, context, instructions, constraints) and best practices for different use cases.

## Key Concepts

- **Four Components**: Every prompt needs Role, Context, Instructions, and Constraints
- **Use Case Adaptation**: Different tasks require different prompt structures
- **Iterative Refinement**: Prompts improve through testing and analysis
- **Template Patterns**: Reusable structures for common scenarios

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Anatomy of a system prompt
make example-2  # Use case variations
make example-3  # Debugging prompts
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
system-prompts/
├── src/system_prompts/
│   ├── __init__.py
│   ├── models.py         # Prompt data models
│   ├── builder.py        # Fluent prompt builder
│   ├── analyzer.py       # Prompt quality analysis
│   ├── templates.py      # Pre-built templates
│   └── examples/
│       ├── example_1.py  # Prompt anatomy
│       ├── example_2.py  # Use case variations
│       └── example_3.py  # Debugging
├── exercises/
│   ├── exercise_1.py     # Code reviewer prompt
│   ├── exercise_2.py     # Vague to precise
│   ├── exercise_3.py     # Template system
│   └── solutions/
├── tests/
│   └── test_examples.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Four-Component Structure
```python
prompt = SystemPrompt(
    role="You are a senior Python developer...",
    context="Working on a Django REST API...",
    instructions="Review code for...",
    constraints="Never suggest removing tests...",
)
```

### Pattern 2: Fluent Builder
```python
prompt = (
    PromptBuilder()
    .with_role("code reviewer")
    .with_expertise(["Python", "security"])
    .with_task("review pull requests")
    .with_constraint("be constructive")
    .build()
)
```

## Common Mistakes

1. **Missing explicit role**
   - AI performs better with clear identity
   - Specify expertise area, not just "helpful"

2. **Instructions without examples**
   - Show, don't just tell
   - Include input/output examples

3. **Constraints that conflict with instructions**
   - Review for logical consistency
   - Test edge cases

## When Users Ask About...

### "How long should a system prompt be?"
Quality over quantity. A focused 200-word prompt beats a rambling 1000-word one. Include only what's necessary for the task.

### "Should I include examples in the prompt?"
Yes, when possible. Examples clarify expectations better than abstract descriptions.

### "How do I test if my prompt works?"
Create a test suite with varied inputs including edge cases. Track success rate and failure patterns.

### "Can I use the same prompt for different models?"
Models have different capabilities. Test and adjust for each. Claude, GPT-4, and others may need different phrasing.

## Testing Notes

- Tests validate prompt structure and analysis
- Example prompts are tested for quality scores
- Run `make test` to verify examples work

## Dependencies

Key dependencies in pyproject.toml:
- pydantic: Prompt data validation
- rich: Terminal output formatting
