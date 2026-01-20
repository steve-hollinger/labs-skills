# CLAUDE.md - OpenAI Responses API

This skill teaches OpenAI API integration including chat completions, function calling, structured outputs, and production patterns.

## Key Concepts

- **Chat Completions**: Core API for conversational AI with message history
- **Function Calling**: Enable models to call your functions with structured arguments
- **Structured Outputs**: Force valid JSON responses using Pydantic schemas
- **Streaming**: Real-time token-by-token response delivery
- **Error Handling**: Rate limits, retries, and graceful degradation
- **Token Management**: Tracking usage and optimizing costs

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run chat completion example
make example-2  # Run function calling example
make example-3  # Run structured outputs example
make example-4  # Run production patterns example
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
openai-responses-api/
├── src/openai_responses_api/
│   ├── __init__.py
│   └── examples/
│       ├── example_1_chat_completion.py
│       ├── example_2_function_calling.py
│       ├── example_3_structured_outputs.py
│       └── example_4_production_patterns.py
├── exercises/
│   ├── exercise_1_chatbot.py
│   ├── exercise_2_tool_agent.py
│   ├── exercise_3_data_extractor.py
│   └── solutions/
├── tests/
│   ├── test_examples.py
│   └── conftest.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Basic Chat Completion
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

### Pattern 2: Function Calling
```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_data",
        "description": "Get data from database",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        }
    }
}]

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

if response.choices[0].message.tool_calls:
    # Handle tool call
    pass
```

### Pattern 3: Structured Output with Pydantic
```python
from pydantic import BaseModel

class Response(BaseModel):
    answer: str
    confidence: float

response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=messages,
    response_format=Response
)
result: Response = response.choices[0].message.parsed
```

### Pattern 4: Streaming with Error Handling
```python
from openai import OpenAI, RateLimitError
from tenacity import retry, wait_exponential

@retry(wait=wait_exponential(min=1, max=60))
def stream_response(messages):
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True
    )
    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

## Common Mistakes

1. **Not setting OPENAI_API_KEY**
   - Set via environment variable or pass to client
   - `client = OpenAI(api_key="sk-...")`

2. **Ignoring rate limits**
   - Always implement exponential backoff
   - Use tenacity library for retries

3. **Not tracking token usage**
   - Check `response.usage.total_tokens`
   - Monitor costs in production

4. **Using wrong model for task**
   - gpt-4o-mini for most tasks (fast, cheap)
   - gpt-4o for complex reasoning
   - Check context window limits

5. **Not using structured outputs for JSON**
   - Use `response_format` parameter
   - Pydantic models ensure valid responses

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make example-1` and README.md. Ensure OPENAI_API_KEY is set.

### "Why am I getting rate limit errors?"
1. Implement exponential backoff with tenacity
2. Check your API tier limits
3. Add delays between requests
4. Consider request batching

### "How do I reduce costs?"
1. Use gpt-4o-mini instead of gpt-4o when possible
2. Reduce max_tokens to needed amount
3. Use shorter system prompts
4. Cache common responses
5. Batch requests when possible

### "How do I get consistent JSON responses?"
Use structured outputs:
```python
client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=messages,
    response_format=YourPydanticModel
)
```

### "How do I implement function calling?"
1. Define tools array with function schemas
2. Pass tools to chat.completions.create
3. Check response for tool_calls
4. Execute function and return result
5. Send result back in follow-up message

## Testing Notes

- Tests use pytest with async support
- Mock OpenAI client for unit tests
- Use respx or httpx mocking
- Integration tests need real API key

## Dependencies

Key dependencies in pyproject.toml:
- openai>=1.0.0: Official OpenAI Python client
- pydantic>=2.0: Data validation for structured outputs
- tenacity: Retry with exponential backoff
- httpx: HTTP client (OpenAI dependency)

## Environment Variables

```bash
OPENAI_API_KEY=sk-...           # Required - API key
OPENAI_ORG_ID=org-...           # Optional - Organization ID
OPENAI_BASE_URL=...             # Optional - Custom endpoint
```

## Model Selection Guide

| Scenario | Recommended Model |
|----------|-------------------|
| General chat | gpt-4o-mini |
| Complex reasoning | gpt-4o |
| Code generation | gpt-4o |
| Simple classification | gpt-4o-mini |
| Long context (>32K) | gpt-4o or gpt-4o-mini |
| Vision/images | gpt-4o |
| Cost-sensitive | gpt-4o-mini |
