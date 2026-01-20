# CLAUDE.md - Four-Layer Prompt Architecture

This skill teaches structured prompt organization using a four-layer pattern that separates system identity, context, instructions, and constraints for maintainable LLM applications.

## Key Concepts

- **System Layer**: Defines AI identity, capabilities, personality, and global behavior
- **Context Layer**: Provides background information, data, and situational awareness
- **Instruction Layer**: Contains specific tasks, actions, or queries to perform
- **Constraint Layer**: Specifies output format, limitations, and guardrails
- **Prompt Composition**: Combining layers dynamically based on use case
- **Template Management**: Reusable layer templates with variable substitution

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run basic four-layer example
make example-2  # Run template management example
make example-3  # Run composition patterns example
make example-4  # Run version management example
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
four-layer-prompts/
├── src/four_layer_prompts/
│   ├── __init__.py
│   ├── layers.py          # Layer classes and builders
│   ├── templates.py       # Template management
│   ├── composer.py        # Prompt composition utilities
│   └── examples/
│       ├── example_1_basic_layers.py
│       ├── example_2_template_management.py
│       ├── example_3_composition_patterns.py
│       └── example_4_version_management.py
├── exercises/
│   ├── exercise_1_code_review.py
│   ├── exercise_2_dynamic_context.py
│   ├── exercise_3_multi_template.py
│   └── solutions/
├── tests/
│   ├── test_layers.py
│   └── test_composer.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Basic Layer Definition
```python
from pydantic import BaseModel

class PromptLayers(BaseModel):
    system: str
    context: str
    instruction: str
    constraint: str

    def compose(self) -> str:
        return f"{self.system}\n\n{self.context}\n\n{self.instruction}\n\n{self.constraint}"
```

### Pattern 2: Template with Variables
```python
from string import Template

system_template = Template("""
You are a $role specializing in $specialty.
You communicate in a $tone tone.
""")

system = system_template.substitute(
    role="technical writer",
    specialty="API documentation",
    tone="professional"
)
```

### Pattern 3: Layer Builder
```python
class PromptBuilder:
    def __init__(self):
        self._layers = {}

    def with_system(self, system: str) -> "PromptBuilder":
        self._layers["system"] = system
        return self

    def with_context(self, context: str) -> "PromptBuilder":
        self._layers["context"] = context
        return self

    def with_instruction(self, instruction: str) -> "PromptBuilder":
        self._layers["instruction"] = instruction
        return self

    def with_constraint(self, constraint: str) -> "PromptBuilder":
        self._layers["constraint"] = constraint
        return self

    def build(self) -> str:
        return "\n\n".join(
            self._layers.get(layer, "")
            for layer in ["system", "context", "instruction", "constraint"]
            if self._layers.get(layer)
        )
```

### Pattern 4: Conditional Layer Composition
```python
def compose_prompt(
    user_level: str,
    task: str,
    include_examples: bool = False
) -> str:
    builder = PromptBuilder()

    # Always include system
    builder.with_system(EXPERT_SYSTEM)

    # Context varies by user level
    if user_level == "beginner":
        builder.with_context(BEGINNER_CONTEXT)
    else:
        builder.with_context(ADVANCED_CONTEXT)

    # Task is always included
    builder.with_instruction(task)

    # Constraints vary
    constraints = [BASE_CONSTRAINTS]
    if include_examples:
        constraints.append("Include at least 2 examples.")
    builder.with_constraint("\n".join(constraints))

    return builder.build()
```

## Common Mistakes

1. **Mixing layer purposes**
   - Keep identity in system, data in context, actions in instruction
   - Constraints should only specify output requirements

2. **Overly long system layers**
   - System layer should be concise (2-5 sentences)
   - Move detailed background to context layer

3. **Hardcoding context**
   - Context should be dynamic and data-driven
   - Use templates with variable substitution

4. **Missing constraints**
   - Always specify output format
   - Include length/scope limitations

5. **Not versioning prompts**
   - Track prompt versions for reproducibility
   - A/B test different layer combinations

## When Users Ask About...

### "How do I structure a new prompt?"
Start with these questions:
1. What identity/personality does the AI need? -> System
2. What data/background is needed? -> Context
3. What specific task should it do? -> Instruction
4. What format/limits apply? -> Constraint

### "My prompt isn't working well"
Debug layer by layer:
1. Is the system layer appropriate for the task?
2. Does the context provide enough information?
3. Is the instruction clear and specific?
4. Are constraints realistic and clear?

### "How do I make prompts reusable?"
Use templates:
1. Define layer templates with placeholders
2. Create a template library by domain
3. Compose prompts by combining templates
4. Version templates for reproducibility

### "How long should each layer be?"
General guidelines:
- System: 50-200 tokens (identity + capabilities)
- Context: Variable (as much as needed, but relevant)
- Instruction: 50-150 tokens (clear, specific)
- Constraint: 30-100 tokens (output requirements)

## Testing Notes

- Tests verify layer composition and template substitution
- Use pytest fixtures for common layer configurations
- Test edge cases (empty layers, missing variables)
- Integration tests can verify prompt effectiveness

## Dependencies

Key dependencies in pyproject.toml:
- pydantic>=2.5.0: Data validation for prompt structures
- jinja2>=3.1.0: Advanced templating support
- pytest>=8.0.0: Testing framework
