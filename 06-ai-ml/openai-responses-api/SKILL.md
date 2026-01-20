---
name: using-openai-responses-api
description: This skill teaches OpenAI API integration including chat completions, function calling, structured outputs, and production patterns. Use when writing or improving tests.
---

# Openai Responses Api

## Quick Start
```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)
content = response.choices[0].message.content
```

## Commands
```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run chat completion example
make example-2  # Run function calling example
make example-3  # Run structured outputs example
make example-4  # Run production patterns example
```

## Key Points
- Chat Completions
- Function Calling
- Structured Outputs

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples