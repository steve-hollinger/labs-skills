---
name: crafting-system-prompts
description: This skill teaches prompt engineering for system prompts, focusing on the four-component structure (role, context, instructions, constraints) and best practices for different use cases. Use when writing or improving tests.
---

# System Prompts

## Quick Start
```python
prompt = SystemPrompt(
    role="You are a senior Python developer...",
    context="Working on a Django REST API...",
    instructions="Review code for...",
    constraints="Never suggest removing tests...",
)
```

## Commands
```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Anatomy of a system prompt
make example-2  # Use case variations
make example-3  # Debugging prompts
make test       # Run pytest
```

## Key Points
- Four Components
- Use Case Adaptation
- Iterative Refinement

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples