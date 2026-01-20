# OpenAI Responses API

Master OpenAI API integration for building AI-powered applications. Learn chat completions, function calling, structured outputs, and production-ready patterns.

## Learning Objectives

After completing this skill, you will be able to:
- Use the OpenAI API for chat completions
- Implement function calling for tool use
- Generate structured outputs with JSON mode
- Handle errors, rate limits, and retries
- Stream responses for better user experience
- Implement cost-effective API usage patterns

## Prerequisites

- Python 3.11+
- UV package manager
- OpenAI API key
- [Pydantic v2](../../01-language-frameworks/python/pydantic-v2/) skill recommended

## Quick Start

```bash
# Install dependencies
make setup

# Set your API key
export OPENAI_API_KEY=your-key-here

# Run examples
make examples

# Run tests
make test
```

## Concepts

### Chat Completions

The core API for conversational AI interactions.

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    temperature=0.7,
    max_tokens=500
)

print(response.choices[0].message.content)
```

### Function Calling

Enable the model to call your functions with structured arguments.

```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["location"]
        }
    }
}]

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
    tools=tools,
    tool_choice="auto"
)

# Handle tool calls
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    args = json.loads(tool_call.function.arguments)
    # Execute your function with args
```

### Structured Outputs

Force the model to return valid JSON matching a schema.

```python
from pydantic import BaseModel

class Analysis(BaseModel):
    sentiment: str
    confidence: float
    keywords: list[str]

response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Analyze: Great product!"}],
    response_format=Analysis
)

result: Analysis = response.choices[0].message.parsed
print(f"Sentiment: {result.sentiment}, Confidence: {result.confidence}")
```

### Streaming

Stream responses for real-time output.

```python
stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

## Examples

### Example 1: Basic Chat Completion

Simple chat interactions with message history management.

```bash
make example-1
```

### Example 2: Function Calling

Build an assistant that uses tools to answer questions.

```bash
make example-2
```

### Example 3: Structured Outputs

Generate validated JSON responses with Pydantic models.

```bash
make example-3
```

### Example 4: Production Patterns

Error handling, retries, rate limiting, and cost tracking.

```bash
make example-4
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Build a Chatbot - Create a conversational assistant with history
2. **Exercise 2**: Tool-Using Agent - Implement function calling for a specific domain
3. **Exercise 3**: Data Extractor - Use structured outputs to parse unstructured text

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## API Models

| Model | Use Case | Context | Cost |
|-------|----------|---------|------|
| gpt-4o | Best quality, multimodal | 128K | $$ |
| gpt-4o-mini | Fast, affordable | 128K | $ |
| gpt-4-turbo | Previous generation | 128K | $$$ |
| gpt-3.5-turbo | Legacy, very fast | 16K | $ |

## Common Mistakes

### Not Handling Rate Limits

Always implement exponential backoff:

```python
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(wait=wait_exponential(min=1, max=60), stop=stop_after_attempt(5))
def call_openai(messages):
    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
```

### Ignoring Token Limits

Track and manage token usage:

```python
response = client.chat.completions.create(...)
print(f"Tokens used: {response.usage.total_tokens}")
print(f"Prompt: {response.usage.prompt_tokens}")
print(f"Completion: {response.usage.completion_tokens}")
```

### Missing Error Handling

Handle specific error types:

```python
from openai import RateLimitError, APIError, AuthenticationError

try:
    response = client.chat.completions.create(...)
except RateLimitError:
    # Wait and retry
    pass
except AuthenticationError:
    # Check API key
    pass
except APIError as e:
    # Log and handle
    pass
```

### Not Using Structured Outputs

For JSON responses, always use response_format:

```python
# Wrong - may return invalid JSON
response = client.chat.completions.create(
    messages=[{"role": "user", "content": "Return JSON..."}]
)

# Correct - guaranteed valid JSON
response = client.beta.chat.completions.parse(
    messages=[...],
    response_format=MyModel
)
```

## Further Reading

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [OpenAI Cookbook](https://github.com/openai/openai-cookbook)
- [Pricing](https://openai.com/pricing)
- Related skills in this repository:
  - [LangChain/LangGraph](../../01-language-frameworks/python/langchain-langgraph/) - Higher-level LLM orchestration
  - [SSE Streaming](../sse-streaming/) - Streaming responses to clients
  - [Pydantic v2](../../01-language-frameworks/python/pydantic-v2/) - Data validation
