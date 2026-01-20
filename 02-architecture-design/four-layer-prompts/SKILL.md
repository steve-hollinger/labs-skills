---
name: structuring-four-layer-prompts
description: This skill teaches structured prompt organization using a four-layer pattern that separates system identity, context, instructions, and constraints for maintainable LLM applications. Use when writing or improving tests.
---

# Four Layer Prompts

## Quick Start
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

## Commands
```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run basic four-layer example
make example-2  # Run template management example
make example-3  # Run composition patterns example
make example-4  # Run version management example
```

## Key Points
- System Layer
- Context Layer
- Instruction Layer

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples