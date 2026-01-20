"""
Example 2: Function Calling

This example demonstrates how to use OpenAI's function calling feature to enable
the model to use tools and execute actions based on user requests.

Key concepts:
- Defining tools with JSON schemas
- Tool choice options
- Handling tool calls in responses
- Multi-turn conversations with tool results
"""

import os
import json
import math
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# ============================================================================
# Tool Implementations
# ============================================================================

def get_weather(location: str, unit: str = "celsius") -> dict:
    """Get weather for a location (mock implementation)."""
    mock_data = {
        "tokyo": {"temp": 22, "condition": "Partly cloudy"},
        "london": {"temp": 15, "condition": "Rainy"},
        "new york": {"temp": 25, "condition": "Sunny"},
        "paris": {"temp": 18, "condition": "Clear"},
    }

    location_lower = location.lower()
    data = mock_data.get(location_lower, {"temp": 20, "condition": "Unknown"})

    temp = data["temp"]
    if unit == "fahrenheit":
        temp = temp * 9/5 + 32

    return {
        "location": location,
        "temperature": temp,
        "unit": unit,
        "condition": data["condition"]
    }


def calculate(expression: str) -> dict:
    """Calculate a mathematical expression."""
    allowed = {
        "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
        "tan": math.tan, "log": math.log, "exp": math.exp,
        "pow": pow, "abs": abs, "round": round,
        "pi": math.pi, "e": math.e
    }
    try:
        result = eval(expression.replace("^", "**"), {"__builtins__": {}}, allowed)
        return {"expression": expression, "result": result}
    except Exception as e:
        return {"expression": expression, "error": str(e)}


def get_current_time(timezone: str = "UTC") -> dict:
    """Get current date and time."""
    return {
        "timezone": timezone,
        "datetime": datetime.now().isoformat(),
        "formatted": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def search_products(query: str, category: str = None, max_results: int = 5) -> dict:
    """Search for products (mock implementation)."""
    mock_products = [
        {"name": "Laptop Pro", "price": 1299, "category": "electronics"},
        {"name": "Wireless Mouse", "price": 49, "category": "electronics"},
        {"name": "Coffee Maker", "price": 89, "category": "kitchen"},
        {"name": "Running Shoes", "price": 129, "category": "sports"},
        {"name": "Desk Chair", "price": 299, "category": "furniture"},
    ]

    results = mock_products
    if category:
        results = [p for p in results if p["category"] == category.lower()]
    if query:
        results = [p for p in results if query.lower() in p["name"].lower()]

    return {
        "query": query,
        "category": category,
        "results": results[:max_results],
        "total_found": len(results)
    }


# Map function names to implementations
TOOL_FUNCTIONS = {
    "get_weather": get_weather,
    "calculate": calculate,
    "get_current_time": get_current_time,
    "search_products": search_products,
}


# ============================================================================
# Tool Definitions
# ============================================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a specific location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city name, e.g., 'Tokyo' or 'New York'"
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
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform mathematical calculations",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate, e.g., '2 + 2' or 'sqrt(16)'"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current date and time",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "Timezone (default: UTC)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Search for products in the catalog",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["electronics", "kitchen", "sports", "furniture"],
                        "description": "Product category filter"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    }
]


# ============================================================================
# Client Setup
# ============================================================================

def get_client():
    """Get OpenAI client or mock."""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("Note: OPENAI_API_KEY not set. Using mock client.")
        return MockClient()

    from openai import OpenAI
    return OpenAI()


class MockClient:
    """Mock client that simulates tool calling."""

    class Completions:
        def create(self, **kwargs):
            messages = kwargs.get("messages", [])
            tools = kwargs.get("tools", [])

            user_msg = next(
                (m["content"] for m in reversed(messages) if m["role"] == "user"),
                ""
            ).lower()

            # Check if this is a follow-up after tool results
            if any(m.get("role") == "tool" for m in messages):
                tool_results = [m for m in messages if m.get("role") == "tool"]
                results_text = "\n".join(m.get("content", "") for m in tool_results)
                return MockResponse(
                    content=f"Based on the tool results:\n{results_text}",
                    tool_calls=None
                )

            # Simulate tool selection
            tool_calls = []
            if "weather" in user_msg:
                location = "Tokyo"
                for city in ["tokyo", "london", "new york", "paris"]:
                    if city in user_msg:
                        location = city.title()
                        break
                tool_calls.append({
                    "id": "call_1",
                    "function": {
                        "name": "get_weather",
                        "arguments": json.dumps({"location": location, "unit": "celsius"})
                    }
                })
            elif "calculate" in user_msg or any(c.isdigit() for c in user_msg):
                tool_calls.append({
                    "id": "call_2",
                    "function": {
                        "name": "calculate",
                        "arguments": json.dumps({"expression": "2 + 2"})
                    }
                })
            elif "time" in user_msg:
                tool_calls.append({
                    "id": "call_3",
                    "function": {
                        "name": "get_current_time",
                        "arguments": json.dumps({})
                    }
                })
            elif "product" in user_msg or "search" in user_msg:
                tool_calls.append({
                    "id": "call_4",
                    "function": {
                        "name": "search_products",
                        "arguments": json.dumps({"query": "laptop"})
                    }
                })

            if tool_calls:
                return MockResponse(content=None, tool_calls=tool_calls)
            else:
                return MockResponse(
                    content=f"[Mock] I received: '{user_msg}'. No tool needed.",
                    tool_calls=None
                )

    def __init__(self):
        self.chat = type("Chat", (), {"completions": self.Completions()})()


class MockResponse:
    def __init__(self, content, tool_calls):
        message = type("Message", (), {
            "content": content,
            "role": "assistant",
            "tool_calls": [
                type("ToolCall", (), {
                    "id": tc["id"],
                    "type": "function",
                    "function": type("Function", (), {
                        "name": tc["function"]["name"],
                        "arguments": tc["function"]["arguments"]
                    })()
                })() for tc in (tool_calls or [])
            ] if tool_calls else None
        })()
        self.choices = [type("Choice", (), {"message": message, "finish_reason": "stop"})()]


# ============================================================================
# Main Function Calling Logic
# ============================================================================

def process_with_tools(client, user_message: str, tools: list = TOOLS) -> str:
    """Process a user message, handling any tool calls."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant with access to tools."},
        {"role": "user", "content": user_message}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message

    # If no tool calls, return the content directly
    if not message.tool_calls:
        return message.content

    # Process tool calls
    print(f"  [Tool calls detected: {len(message.tool_calls)}]")
    messages.append({
        "role": "assistant",
        "content": message.content,
        "tool_calls": [
            {
                "id": tc.id,
                "type": "function",
                "function": {"name": tc.function.name, "arguments": tc.function.arguments}
            } for tc in message.tool_calls
        ]
    })

    for tool_call in message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        print(f"  [Calling {function_name} with {arguments}]")

        # Execute the function
        if function_name in TOOL_FUNCTIONS:
            result = TOOL_FUNCTIONS[function_name](**arguments)
        else:
            result = {"error": f"Unknown function: {function_name}"}

        # Add tool result to messages
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result)
        })

    # Get final response with tool results
    final_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    return final_response.choices[0].message.content


# ============================================================================
# Examples
# ============================================================================

def example_basic_tool_use():
    """Basic tool calling example."""
    print("\n--- Basic Tool Use ---")

    client = get_client()

    queries = [
        "What's the weather like in Tokyo?",
        "Calculate the square root of 256",
        "What time is it?",
        "Search for laptop products",
    ]

    for query in queries:
        print(f"\nUser: {query}")
        response = process_with_tools(client, query)
        print(f"Assistant: {response}")


def example_multi_tool():
    """Example with multiple tool calls in one request."""
    print("\n--- Multiple Tool Calls ---")

    client = get_client()

    query = "What's the weather in Tokyo and what time is it there?"
    print(f"\nUser: {query}")
    response = process_with_tools(client, query)
    print(f"Assistant: {response}")


def example_tool_choice():
    """Demonstrate tool_choice options."""
    print("\n--- Tool Choice Options ---")

    client = get_client()

    if not os.getenv("OPENAI_API_KEY"):
        print("  Skipping tool_choice demo (requires real API)")
        return

    from openai import OpenAI
    client = OpenAI()

    messages = [
        {"role": "user", "content": "Tell me about the weather"}
    ]

    # Auto - model decides
    print("\ntool_choice='auto' (model decides):")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto"
    )
    has_tools = bool(response.choices[0].message.tool_calls)
    print(f"  Used tools: {has_tools}")

    # Required - must use a tool
    print("\ntool_choice='required' (must use a tool):")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOLS,
        tool_choice="required"
    )
    print(f"  Tool used: {response.choices[0].message.tool_calls[0].function.name}")

    # Specific tool - force a specific function
    print("\ntool_choice={'function': 'get_current_time'} (force specific):")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOLS,
        tool_choice={"type": "function", "function": {"name": "get_current_time"}}
    )
    print(f"  Tool used: {response.choices[0].message.tool_calls[0].function.name}")


def main():
    """Run all function calling examples."""
    print("=" * 60)
    print("Example 2: Function Calling")
    print("=" * 60)

    example_basic_tool_use()
    example_multi_tool()
    example_tool_choice()

    print("\n" + "=" * 60)
    print("Key Takeaways:")
    print("1. Define tools with JSON schemas for parameters")
    print("2. Model returns tool_calls when it wants to use a tool")
    print("3. Execute functions and send results back")
    print("4. Use tool_choice to control tool usage behavior")
    print("=" * 60)


if __name__ == "__main__":
    main()
