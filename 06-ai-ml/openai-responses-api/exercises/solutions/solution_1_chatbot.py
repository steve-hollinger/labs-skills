"""
Solution 1: Conversational Chatbot

A complete chatbot implementation with history management and token tracking.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Chatbot:
    """A conversational chatbot with history management."""

    def __init__(self, system_prompt: str = "You are a helpful assistant.",
                 temperature: float = 0.7):
        """Initialize the chatbot."""
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.messages = [{"role": "system", "content": system_prompt}]
        self.total_tokens = 0
        self._client = self._get_client()

    def _get_client(self):
        """Get OpenAI client or None for mock mode."""
        if not os.getenv("OPENAI_API_KEY"):
            return None
        from openai import OpenAI
        return OpenAI()

    def chat(self, user_message: str) -> str:
        """Send a message and get a response."""
        # Add user message to history
        self.messages.append({"role": "user", "content": user_message})

        if self._client is None:
            # Mock response
            response_content = f"[Mock] You said: '{user_message}'. I'm here to help!"
            self.messages.append({"role": "assistant", "content": response_content})
            self.total_tokens += len(user_message.split()) + len(response_content.split())
            return response_content

        # Call OpenAI API
        response = self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.messages,
            temperature=self.temperature
        )

        # Extract response
        assistant_message = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": assistant_message})

        # Update token count
        self.total_tokens += response.usage.total_tokens

        return assistant_message

    def clear_history(self):
        """Clear conversation history, keeping system prompt."""
        self.messages = [{"role": "system", "content": self.system_prompt}]
        self.total_tokens = 0

    def get_history(self) -> list:
        """Get the current conversation history."""
        return self.messages.copy()

    def get_token_usage(self) -> int:
        """Get total tokens used in this conversation."""
        return self.total_tokens


# Test the implementation
if __name__ == "__main__":
    print("Testing Chatbot Implementation")
    print("=" * 50)

    # Test 1: Basic conversation
    print("\nTest 1: Basic conversation")
    bot = Chatbot(system_prompt="You are a friendly assistant named Max.")

    response1 = bot.chat("Hi! What's your name?")
    print(f"User: Hi! What's your name?")
    print(f"Bot: {response1}")

    response2 = bot.chat("Nice to meet you! What can you help me with?")
    print(f"User: Nice to meet you! What can you help me with?")
    print(f"Bot: {response2}")

    # Test 2: History retention
    print("\nTest 2: History retention")
    history = bot.get_history()
    print(f"Messages in history: {len(history)}")
    print(f"Total tokens used: {bot.get_token_usage()}")

    # Verify history structure
    expected_roles = ["system", "user", "assistant", "user", "assistant"]
    actual_roles = [m["role"] for m in history]
    print(f"History structure correct: {'PASS' if actual_roles == expected_roles else 'FAIL'}")

    # Test 3: Clear history
    print("\nTest 3: Clear history")
    bot.clear_history()
    history_after_clear = bot.get_history()
    print(f"Messages after clear: {len(history_after_clear)}")
    print(f"Should be 1 (system message only): {'PASS' if len(history_after_clear) == 1 else 'FAIL'}")
    print(f"Token counter reset: {'PASS' if bot.get_token_usage() == 0 else 'FAIL'}")

    # Test 4: Temperature effect
    print("\nTest 4: Different temperatures")
    creative_bot = Chatbot(
        system_prompt="You are a creative storyteller.",
        temperature=1.2
    )
    focused_bot = Chatbot(
        system_prompt="You are a precise assistant.",
        temperature=0.2
    )

    prompt = "Describe a sunset in one sentence."
    print(f"Prompt: {prompt}")
    print(f"Creative (temp=1.2): {creative_bot.chat(prompt)}")
    print(f"Focused (temp=0.2): {focused_bot.chat(prompt)}")

    # Test 5: Multi-turn context
    print("\nTest 5: Multi-turn context retention")
    context_bot = Chatbot(system_prompt="You remember everything the user tells you.")
    context_bot.chat("My favorite color is blue.")
    context_bot.chat("I have a dog named Buddy.")
    response = context_bot.chat("What's my favorite color and pet's name?")
    print(f"Context test response: {response}")

    print("\n" + "=" * 50)
    print("All tests completed!")
