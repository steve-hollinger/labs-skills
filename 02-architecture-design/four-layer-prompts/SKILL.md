---
name: structuring-four-layer-prompts
description: Structured prompt organization using a four-layer pattern that separates system identity, context, instructions, and constraints for maintainable LLM applications. Use when writing or improving tests.
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


## Key Points
- System Layer
- Context Layer
- Instruction Layer

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples