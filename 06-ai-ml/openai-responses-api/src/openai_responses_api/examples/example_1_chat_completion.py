"""
Example 1: Chat Completions

This example demonstrates the fundamentals of the OpenAI Chat Completions API
including basic usage, message history, and parameter configuration.

Key concepts:
- Creating the OpenAI client
- Message roles (system, user, assistant)
- API parameters (temperature, max_tokens)
- Handling responses and token usage
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_client():
    """Get OpenAI client, falling back to mock if no API key."""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("Note: OPENAI_API_KEY not set. Using mock client.")
        return MockOpenAIClient()

    from openai import OpenAI
    return OpenAI()


class MockOpenAIClient:
    """Mock client for demonstration without API key."""

    class Completions:
        def create(self, **kwargs):
            return MockResponse(kwargs.get("messages", []))

    def __init__(self):
        self.chat = type("Chat", (), {"completions": self.Completions()})()


class MockResponse:
    """Mock response object."""

    def __init__(self, messages):
        user_msg = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"),
            "Hello"
        )
        self.choices = [
            type("Choice", (), {
                "message": type("Message", (), {
                    "content": f"[Mock Response] You said: '{user_msg}'. This is a simulated response.",
                    "role": "assistant"
                })(),
                "finish_reason": "stop"
            })()
        ]
        self.usage = type("Usage", (), {
            "prompt_tokens": len(str(messages)) // 4,
            "completion_tokens": 20,
            "total_tokens": len(str(messages)) // 4 + 20
        })()
        self.model = "mock-model"


def basic_chat_completion():
    """Demonstrate basic chat completion."""
    print("\n--- Basic Chat Completion ---")

    client = get_client()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is Python in one sentence?"}
        ],
        temperature=0.7,
        max_tokens=100
    )

    print(f"Response: {response.choices[0].message.content}")
    print(f"Tokens used: {response.usage.total_tokens}")


def chat_with_history():
    """Demonstrate maintaining conversation history."""
    print("\n--- Chat with History ---")

    client = get_client()

    # Build conversation history
    messages = [
        {"role": "system", "content": "You are a friendly assistant who remembers context."}
    ]

    # First turn
    messages.append({"role": "user", "content": "My name is Alice."})
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=100
    )
    assistant_reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_reply})
    print(f"User: My name is Alice.")
    print(f"Assistant: {assistant_reply}")

    # Second turn - should remember the name
    messages.append({"role": "user", "content": "What's my name?"})
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=100
    )
    print(f"User: What's my name?")
    print(f"Assistant: {response.choices[0].message.content}")


def parameter_exploration():
    """Demonstrate different API parameters."""
    print("\n--- Parameter Exploration ---")

    client = get_client()
    prompt = "Write a creative one-line tagline for a coffee shop."

    # Low temperature - more focused/deterministic
    print("\nLow temperature (0.2) - More focused:")
    for i in range(2):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=50
        )
        print(f"  {i+1}. {response.choices[0].message.content}")

    # High temperature - more creative/varied
    print("\nHigh temperature (1.2) - More creative:")
    for i in range(2):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=1.2,
            max_tokens=50
        )
        print(f"  {i+1}. {response.choices[0].message.content}")


def system_prompt_examples():
    """Demonstrate the impact of system prompts."""
    print("\n--- System Prompt Impact ---")

    client = get_client()
    user_message = "Tell me about cats."

    system_prompts = [
        ("Scientist", "You are a scientist who explains things technically."),
        ("Poet", "You are a poet who speaks in verse and metaphor."),
        ("Pirate", "You are a pirate who speaks in pirate slang."),
    ]

    for persona, system_prompt in system_prompts:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=100,
            temperature=0.7
        )
        print(f"\n{persona}:")
        print(f"  {response.choices[0].message.content[:200]}...")


def token_usage_tracking():
    """Demonstrate tracking token usage for cost management."""
    print("\n--- Token Usage Tracking ---")

    client = get_client()

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing in simple terms."}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=200
    )

    usage = response.usage
    print(f"Prompt tokens: {usage.prompt_tokens}")
    print(f"Completion tokens: {usage.completion_tokens}")
    print(f"Total tokens: {usage.total_tokens}")

    # Estimate cost (gpt-4o-mini pricing)
    input_cost = (usage.prompt_tokens / 1_000_000) * 0.15
    output_cost = (usage.completion_tokens / 1_000_000) * 0.60
    total_cost = input_cost + output_cost
    print(f"Estimated cost: ${total_cost:.6f}")


def main():
    """Run all chat completion examples."""
    print("=" * 60)
    print("Example 1: Chat Completions")
    print("=" * 60)

    basic_chat_completion()
    chat_with_history()
    parameter_exploration()
    system_prompt_examples()
    token_usage_tracking()

    print("\n" + "=" * 60)
    print("Key Takeaways:")
    print("1. Use system messages to set assistant behavior")
    print("2. Maintain message history for context")
    print("3. Adjust temperature for creativity vs consistency")
    print("4. Track token usage for cost management")
    print("=" * 60)


if __name__ == "__main__":
    main()
