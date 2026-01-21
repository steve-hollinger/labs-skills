# Common Patterns

This document covers practical patterns for building applications with the OpenAI API.

## Conversation Patterns

### 1. Simple Chatbot

```python
from openai import OpenAI

class SimpleChatbot:
    def __init__(self, system_prompt: str = "You are a helpful assistant."):
        self.client = OpenAI()
        self.messages = [{"role": "system", "content": system_prompt}]

    def chat(self, user_message: str) -> str:
        self.messages.append({"role": "user", "content": user_message})

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.messages
        )

        assistant_message = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": assistant_message})

        return assistant_message

    def clear_history(self):
        self.messages = [self.messages[0]]  # Keep system message
```

### 2. Conversation with Summary

For long conversations, summarize older messages:

```python
class ConversationWithSummary:
    def __init__(self, max_messages: int = 20):
        self.client = OpenAI()
        self.max_messages = max_messages
        self.messages = []
        self.summary = ""

    def chat(self, user_message: str) -> str:
        messages_to_send = self._build_messages(user_message)

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_to_send
        )

        assistant_message = response.choices[0].message.content
        self.messages.append({"role": "user", "content": user_message})
        self.messages.append({"role": "assistant", "content": assistant_message})

        if len(self.messages) > self.max_messages:
            self._summarize_old_messages()

        return assistant_message

    def _build_messages(self, current_message: str) -> list:
        result = [{"role": "system", "content": "You are a helpful assistant."}]

        if self.summary:
            result.append({
                "role": "system",
                "content": f"Previous conversation summary: {self.summary}"
            })

        result.extend(self.messages)
        result.append({"role": "user", "content": current_message})
        return result

    def _summarize_old_messages(self):
        old_messages = self.messages[:self.max_messages // 2]
        self.messages = self.messages[self.max_messages // 2:]

        summary_response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Summarize this conversation briefly."},
                {"role": "user", "content": str(old_messages)}
            ]
        )

        new_summary = summary_response.choices[0].message.content
        self.summary = f"{self.summary}\n{new_summary}" if self.summary else new_summary
```

## Function Calling Patterns

### 1. Multi-Tool Agent

```python
import json

class MultiToolAgent:
    def __init__(self):
        self.client = OpenAI()
        self.tools = self._define_tools()
        self.tool_functions = {
            "search": self._search,
            "calculate": self._calculate,
            "get_date": self._get_date,
        }

    def _define_tools(self) -> list:
        return [
            {
                "type": "function",
                "function": {
                    "name": "search",
                    "description": "Search for information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate",
                    "description": "Perform calculations",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {"type": "string"}
                        },
                        "required": ["expression"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_date",
                    "description": "Get current date/time",
                    "parameters": {"type": "object", "properties": {}}
                }
            }
        ]

    def process(self, user_message: str) -> str:
        messages = [{"role": "user", "content": user_message}]

        while True:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )

            message = response.choices[0].message

            if not message.tool_calls:
                return message.content

            messages.append(message)

            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                result = self.tool_functions[function_name](**arguments)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })

    def _search(self, query: str) -> str:
        return f"Search results for: {query}"

    def _calculate(self, expression: str) -> str:
        try:
            return str(eval(expression))
        except Exception as e:
            return f"Error: {e}"

    def _get_date(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()
```

### 2. Function Calling with Confirmation

```python
class ConfirmingAgent:
    """Agent that confirms before executing sensitive operations."""

    def __init__(self):
        self.client = OpenAI()
        self.pending_action = None

    def process(self, user_message: str) -> dict:
        if self.pending_action and user_message.lower() in ["yes", "confirm"]:
            result = self._execute_action(self.pending_action)
            self.pending_action = None
            return {"type": "result", "content": result}

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_message}],
            tools=self._get_tools()
        )

        message = response.choices[0].message

        if message.tool_calls:
            action = {
                "function": message.tool_calls[0].function.name,
                "arguments": json.loads(message.tool_calls[0].function.arguments)
            }

            if self._requires_confirmation(action["function"]):
                self.pending_action = action
                return {
                    "type": "confirmation_needed",
                    "content": f"Confirm {action['function']} with {action['arguments']}?"
                }

            return {"type": "result", "content": self._execute_action(action)}

        return {"type": "response", "content": message.content}

    def _requires_confirmation(self, function_name: str) -> bool:
        sensitive_functions = ["delete", "send_email", "make_payment"]
        return function_name in sensitive_functions
```

## Structured Output Patterns

### 1. Data Extraction Pipeline

```python
from pydantic import BaseModel, Field
from typing import Optional

class ContactInfo(BaseModel):
    name: Optional[str] = Field(None, description="Person's name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    company: Optional[str] = Field(None, description="Company name")

class DataExtractor:
    def __init__(self):
        self.client = OpenAI()

    def extract_contacts(self, text: str) -> list[ContactInfo]:
        class ContactList(BaseModel):
            contacts: list[ContactInfo]

        response = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Extract contact information from text."},
                {"role": "user", "content": text}
            ],
            response_format=ContactList
        )

        return response.choices[0].message.parsed.contacts
```

### 2. Classification with Confidence

```python
from pydantic import BaseModel, Field
from enum import Enum

class Category(str, Enum):
    technical = "technical"
    billing = "billing"
    general = "general"
    complaint = "complaint"

class Classification(BaseModel):
    category: Category
    confidence: float = Field(ge=0, le=1)
    reasoning: str

class Classifier:
    def __init__(self):
        self.client = OpenAI()

    def classify(self, text: str) -> Classification:
        response = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Classify the following text into a category. "
                               "Provide confidence (0-1) and brief reasoning."
                },
                {"role": "user", "content": text}
            ],
            response_format=Classification
        )

        return response.choices[0].message.parsed
```

## Production Patterns

### 1. Rate-Limited Client

```python
import time
from threading import Lock
from collections import deque

class RateLimitedClient:
    def __init__(self, requests_per_minute: int = 60):
        self.client = OpenAI()
        self.rpm = requests_per_minute
        self.request_times = deque()
        self.lock = Lock()

    def _wait_for_rate_limit(self):
        with self.lock:
            now = time.time()

            # Remove requests older than 1 minute
            while self.request_times and self.request_times[0] < now - 60:
                self.request_times.popleft()

            if len(self.request_times) >= self.rpm:
                sleep_time = 60 - (now - self.request_times[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)

            self.request_times.append(time.time())

    def chat(self, messages: list, **kwargs):
        self._wait_for_rate_limit()
        return self.client.chat.completions.create(
            messages=messages,
            **kwargs
        )
```

### 2. Caching Layer

```python
import hashlib
import json
from functools import lru_cache

class CachedClient:
    def __init__(self, cache_size: int = 1000):
        self.client = OpenAI()
        self._cache = {}
        self.cache_size = cache_size

    def _cache_key(self, messages: list, model: str, **kwargs) -> str:
        content = json.dumps({
            "messages": messages,
            "model": model,
            **kwargs
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def chat(self, messages: list, model: str = "gpt-4o-mini", use_cache: bool = True, **kwargs):
        if use_cache:
            key = self._cache_key(messages, model, **kwargs)
            if key in self._cache:
                return self._cache[key]

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )

        if use_cache:
            if len(self._cache) >= self.cache_size:
                # Remove oldest entry
                self._cache.pop(next(iter(self._cache)))
            self._cache[key] = response

        return response
```

### 3. Cost Tracking

```python
class CostTracker:
    # Prices per 1M tokens (as of 2024)
    PRICING = {
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    }

    def __init__(self):
        self.client = OpenAI()
        self.total_cost = 0.0
        self.requests = []

    def chat(self, messages: list, model: str = "gpt-4o-mini", **kwargs):
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )

        cost = self._calculate_cost(response, model)
        self.total_cost += cost
        self.requests.append({
            "model": model,
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "cost": cost
        })

        return response

    def _calculate_cost(self, response, model: str) -> float:
        pricing = self.PRICING.get(model, self.PRICING["gpt-4o-mini"])
        input_cost = (response.usage.prompt_tokens / 1_000_000) * pricing["input"]
        output_cost = (response.usage.completion_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    def get_summary(self) -> dict:
        return {
            "total_cost": f"${self.total_cost:.4f}",
            "total_requests": len(self.requests),
            "total_tokens": sum(r["prompt_tokens"] + r["completion_tokens"] for r in self.requests)
        }
```

### 4. Fallback Chain

```python
class FallbackClient:
    """Try multiple models/configs in sequence."""

    def __init__(self):
        self.client = OpenAI()
        self.fallback_configs = [
            {"model": "gpt-4o-mini", "max_tokens": 1000},
            {"model": "gpt-4o", "max_tokens": 500},
            {"model": "gpt-3.5-turbo", "max_tokens": 1000},
        ]

    def chat(self, messages: list) -> str:
        last_error = None

        for config in self.fallback_configs:
            try:
                response = self.client.chat.completions.create(
                    messages=messages,
                    **config
                )
                return response.choices[0].message.content
            except Exception as e:
                last_error = e
                continue

        raise last_error or Exception("All models failed")
```

## Streaming Patterns

### 1. SSE Generator for Web

```python
async def stream_to_sse(messages: list):
    """Generate SSE events from OpenAI stream."""
    client = OpenAI()

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\n\n"

    yield "data: [DONE]\n\n"
```

### 2. Progress Tracking Stream

```python
class ProgressStream:
    def __init__(self):
        self.client = OpenAI()
        self.total_tokens = 0

    def stream_with_progress(self, messages: list, on_progress=None):
        stream = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=True,
            stream_options={"include_usage": True}
        )

        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                yield content

            if chunk.usage and on_progress:
                on_progress(chunk.usage.total_tokens)

        return full_response
```
