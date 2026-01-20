# Four-Layer Prompt Architecture

Master structured prompt organization for building maintainable, composable LLM applications with clear separation between system context, user context, instructions, and constraints.

## Learning Objectives

After completing this skill, you will be able to:
- Design prompts using the four-layer architecture pattern
- Separate concerns between system, context, instruction, and constraint layers
- Build reusable prompt templates and components
- Implement dynamic prompt composition
- Manage prompt versions and variations effectively

## Prerequisites

- Python 3.11+
- Basic understanding of LLM prompting
- Familiarity with string templating

## Quick Start

```bash
# Install dependencies
make setup

# Run examples
make examples

# Run tests
make test
```

## The Four Layers

### Layer 1: System Layer
Defines the AI's identity, capabilities, and behavioral boundaries.

```python
system_layer = """
You are a professional technical writer specializing in API documentation.
You have expertise in REST APIs, OpenAPI specifications, and developer experience.
You write in a clear, concise style suitable for developer audiences.
"""
```

### Layer 2: Context Layer
Provides background information, data, and situational context.

```python
context_layer = """
The following API endpoint needs documentation:
- Method: POST
- Path: /api/v1/users
- Request Body: {schema}
- Response: {response_schema}

Current documentation standards: {standards_doc}
"""
```

### Layer 3: Instruction Layer
Contains the specific task or action to perform.

```python
instruction_layer = """
Generate comprehensive API documentation for this endpoint including:
1. Endpoint description and purpose
2. Request parameters with types and descriptions
3. Example request/response pairs
4. Error codes and their meanings
5. Authentication requirements
"""
```

### Layer 4: Constraint Layer
Specifies output format, limitations, and guardrails.

```python
constraint_layer = """
Requirements:
- Use markdown formatting
- Keep descriptions under 100 words each
- Include at least 2 example requests
- Do not include internal implementation details
- Output must be valid markdown
"""
```

## Why Four Layers?

| Benefit | Description |
|---------|-------------|
| **Separation of Concerns** | Each layer has a distinct purpose, making prompts easier to maintain |
| **Reusability** | System and constraint layers can be shared across many prompts |
| **Testability** | Individual layers can be validated independently |
| **Composability** | Mix and match layers for different use cases |
| **Debuggability** | Easier to identify which layer causes issues |

## Examples

### Example 1: Basic Four-Layer Prompt

Demonstrates constructing and composing the four layers into a complete prompt.

```bash
make example-1
```

### Example 2: Template Management

Shows how to create reusable templates for each layer with variable substitution.

```bash
make example-2
```

### Example 3: Prompt Composition Patterns

Advanced patterns for building complex prompts from layer components.

```bash
make example-3
```

### Example 4: Version Management

Managing prompt versions and A/B testing different layer configurations.

```bash
make example-4
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Build a Code Review Prompt - Create a four-layer prompt for reviewing code
2. **Exercise 2**: Dynamic Context Injection - Build prompts that adapt to different contexts
3. **Exercise 3**: Multi-Template Composition - Combine multiple templates into complex workflows

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Mixing Concerns Across Layers

```python
# Bad: Instructions mixed with constraints
instruction = """
Write a summary. Keep it under 100 words. Be professional.
"""

# Good: Separated concerns
instruction = "Write a comprehensive summary of the document."
constraint = "Keep the summary under 100 words. Use professional tone."
```

### Overly Rigid System Layers

```python
# Bad: Too specific, limits flexibility
system = "You are a Python expert who only writes FastAPI code."

# Good: Defines expertise while allowing flexibility
system = """
You are a senior software engineer with deep expertise in Python.
You specialize in web frameworks, particularly FastAPI and Django.
"""
```

### Missing Constraint Layer

Always include constraints, even minimal ones:

```python
# Minimal but effective constraint
constraint = """
Output format: JSON
Maximum response length: 500 tokens
"""
```

## Layer Interaction Patterns

### Sequential Enhancement
Each layer builds on previous ones:

```
System -> Context -> Instruction -> Constraint
```

### Override Pattern
Later layers can refine earlier ones:

```python
system = "You are a helpful assistant."  # General
context = "User is a senior developer."   # Adds specificity
instruction = "Explain Python decorators."
constraint = "Skip basic Python syntax explanations."  # Refines based on context
```

### Conditional Layers
Include layers based on conditions:

```python
def build_prompt(user_level: str) -> str:
    layers = [system_layer, instruction_layer]

    if user_level == "beginner":
        layers.insert(1, beginner_context)
        layers.append(beginner_constraints)
    else:
        layers.insert(1, expert_context)
        layers.append(expert_constraints)

    return "\n\n".join(layers)
```

## Further Reading

- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [Anthropic's Prompt Engineering](https://docs.anthropic.com/claude/docs/prompt-engineering)
- Related skills in this repository:
  - [LLM Integration](../../06-ai-ml/llm-integration/)
  - [Template Patterns](../../02-architecture-design/template-patterns/)
