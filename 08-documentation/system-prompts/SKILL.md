---
name: crafting-system-prompts
description: Prompt engineering for system prompts, focusing on the four-component structure (role, context, instructions, constraints) and best practices for different use cases. Use when writing or improving tests.
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


## Key Points
- Four Components
- Use Case Adaptation
- Iterative Refinement

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples