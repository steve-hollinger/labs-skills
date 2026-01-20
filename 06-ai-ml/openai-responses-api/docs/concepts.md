# Core Concepts

This document explains the fundamental concepts of the OpenAI Responses API.

## 1. Chat Completions API

The Chat Completions API is the primary interface for interacting with OpenAI's language models.

### Message Structure

Messages have three roles:

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi! How can I help?"},
    {"role": "user", "content": "What's the weather?"}
]
```

- **system**: Sets the assistant's behavior and context
- **user**: Human input/questions
- **assistant**: Previous AI responses (for context)

### API Parameters

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",          # Model to use
    messages=messages,             # Conversation history
    temperature=0.7,               # Randomness (0-2, lower = more focused)
    max_tokens=500,                # Maximum response length
    top_p=1.0,                     # Nucleus sampling (alternative to temperature)
    frequency_penalty=0.0,         # Reduce repetition (-2 to 2)
    presence_penalty=0.0,          # Encourage new topics (-2 to 2)
    stop=["\n\n"],                 # Stop sequences
    n=1,                           # Number of completions to generate
)
```

### Response Structure

```python
response.id                              # Unique response ID
response.model                           # Model used
response.choices[0].message.content      # The actual response text
response.choices[0].message.role         # "assistant"
response.choices[0].finish_reason        # "stop", "length", "tool_calls"
response.usage.prompt_tokens             # Tokens in input
response.usage.completion_tokens         # Tokens in output
response.usage.total_tokens              # Total tokens used
```

## 2. Function Calling

Function calling allows the model to invoke your functions with structured arguments.

### Tool Definition

```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and state, e.g., 'San Francisco, CA'"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit"
                }
            },
            "required": ["location"]
        }
    }
}]
```

### Tool Choice Options

```python
# Let model decide whether to use tools
tool_choice="auto"

# Force a specific tool
tool_choice={"type": "function", "function": {"name": "get_weather"}}

# Prevent tool use
tool_choice="none"

# Require some tool (model picks which)
tool_choice="required"
```

### Handling Tool Calls

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools
)

message = response.choices[0].message

if message.tool_calls:
    for tool_call in message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        # Execute your function
        result = your_function(**arguments)

        # Send result back to model
        messages.append(message)  # Include assistant's tool call
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": str(result)
        })

    # Get final response
    final_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
```

### Parallel Tool Calls

The model can call multiple tools in one response:

```python
if message.tool_calls:
    # May contain multiple tool calls
    for tool_call in message.tool_calls:
        # Handle each call
        pass
```

## 3. Structured Outputs

Structured outputs guarantee the model returns valid JSON matching your schema.

### JSON Mode (Basic)

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Return JSON only."},
        {"role": "user", "content": "List 3 colors"}
    ],
    response_format={"type": "json_object"}
)
# Returns valid JSON, but schema not enforced
```

### Structured Output with Pydantic (Recommended)

```python
from pydantic import BaseModel, Field

class ColorList(BaseModel):
    colors: list[str] = Field(description="List of color names")
    count: int = Field(description="Number of colors")

response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "List 3 colors"}],
    response_format=ColorList
)

result: ColorList = response.choices[0].message.parsed
print(result.colors)  # ['red', 'blue', 'green']
print(result.count)   # 3
```

### Complex Schemas

```python
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class Sentiment(str, Enum):
    positive = "positive"
    negative = "negative"
    neutral = "neutral"

class Entity(BaseModel):
    name: str
    type: str
    confidence: float

class Analysis(BaseModel):
    sentiment: Sentiment
    entities: list[Entity]
    summary: str
    keywords: list[str]
    language: Optional[str] = None
```

## 4. Streaming

Streaming delivers responses token-by-token for better user experience.

### Basic Streaming

```python
stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    stream=True
)

for chunk in stream:
    delta = chunk.choices[0].delta
    if delta.content:
        print(delta.content, end="", flush=True)
```

### Async Streaming

```python
async def stream_response():
    stream = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True
    )

    async for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

### Streaming with Tools

```python
stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools,
    stream=True
)

collected_tool_calls = []
for chunk in stream:
    delta = chunk.choices[0].delta

    # Collect tool call chunks
    if delta.tool_calls:
        for tc in delta.tool_calls:
            # Build up tool call from chunks
            pass

    if delta.content:
        print(delta.content, end="")
```

## 5. Error Handling

### Error Types

```python
from openai import (
    APIError,
    RateLimitError,
    APIConnectionError,
    AuthenticationError,
    BadRequestError,
)

try:
    response = client.chat.completions.create(...)
except AuthenticationError:
    # Invalid API key
    pass
except RateLimitError:
    # Too many requests - implement backoff
    pass
except BadRequestError as e:
    # Invalid request (bad parameters, too many tokens)
    print(f"Bad request: {e.message}")
except APIConnectionError:
    # Network issues
    pass
except APIError as e:
    # Generic API error
    print(f"API error: {e.status_code}")
```

### Retry with Exponential Backoff

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from openai import RateLimitError, APIError

@retry(
    retry=retry_if_exception_type((RateLimitError, APIError)),
    wait=wait_exponential(multiplier=1, min=1, max=60),
    stop=stop_after_attempt(5)
)
def call_with_retry(messages):
    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
```

## 6. Token Management

### Counting Tokens

```python
import tiktoken

def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# Count message tokens
def count_message_tokens(messages: list, model: str = "gpt-4o-mini") -> int:
    encoding = tiktoken.encoding_for_model(model)
    total = 0
    for message in messages:
        total += 4  # Message overhead
        for key, value in message.items():
            total += len(encoding.encode(str(value)))
    total += 2  # Response priming
    return total
```

### Token Limits by Model

| Model | Context Window | Output Limit |
|-------|----------------|--------------|
| gpt-4o | 128,000 | 16,384 |
| gpt-4o-mini | 128,000 | 16,384 |
| gpt-4-turbo | 128,000 | 4,096 |
| gpt-3.5-turbo | 16,385 | 4,096 |

### Managing Long Contexts

```python
def truncate_messages(messages: list, max_tokens: int, model: str) -> list:
    """Keep most recent messages within token limit."""
    result = []
    total_tokens = 0

    # Always keep system message
    system_msg = next((m for m in messages if m["role"] == "system"), None)
    if system_msg:
        total_tokens += count_message_tokens([system_msg], model)
        result.append(system_msg)

    # Add messages from most recent, skip system
    for msg in reversed(messages):
        if msg["role"] == "system":
            continue
        msg_tokens = count_message_tokens([msg], model)
        if total_tokens + msg_tokens > max_tokens:
            break
        result.insert(1, msg)  # Insert after system message
        total_tokens += msg_tokens

    return result
```
