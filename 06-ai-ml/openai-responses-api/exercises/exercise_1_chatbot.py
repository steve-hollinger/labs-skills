"""
Exercise 1: Build a Conversational Chatbot

Create a chatbot class that maintains conversation history and provides
a natural conversational experience.

Requirements:
1. Maintain conversation history across turns
2. Support system prompt configuration
3. Implement clear_history() method
4. Track token usage across the conversation
5. Support temperature configuration

Test your implementation with the provided test cases.

Hints:
- Store messages in a list
- Append both user and assistant messages
- Track cumulative token usage
- System message should always be first
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Chatbot:
    """A conversational chatbot with history management.

    Attributes:
        system_prompt: The system prompt defining chatbot behavior
        temperature: Response randomness (0-2)
        messages: Conversation history
        total_tokens: Cumulative token usage
    """

    def __init__(self, system_prompt: str = "You are a helpful assistant.",
                 temperature: float = 0.7):
        """Initialize the chatbot.

        Args:
            system_prompt: Defines the chatbot's behavior
            temperature: Controls response randomness (0-2)
        """
        # TODO: Initialize the chatbot
        # - Store system_prompt and temperature
        # - Initialize messages list with system message
        # - Initialize total_tokens counter
        # - Create OpenAI client
        pass

    def chat(self, user_message: str) -> str:
        """Send a message and get a response.

        Args:
            user_message: The user's input

        Returns:
            The assistant's response
        """
        # TODO: Implement chat functionality
        # 1. Append user message to history
        # 2. Call OpenAI API with full message history
        # 3. Extract and append assistant response
        # 4. Update token count
        # 5. Return response content
        pass

    def clear_history(self):
        """Clear conversation history, keeping system prompt."""
        # TODO: Reset messages to only contain system message
        # Reset token counter
        pass

    def get_history(self) -> list:
        """Get the current conversation history.

        Returns:
            List of message dictionaries
        """
        # TODO: Return copy of messages list
        pass

    def get_token_usage(self) -> int:
        """Get total tokens used in this conversation.

        Returns:
            Total token count
        """
        # TODO: Return total_tokens
        pass


# Test your implementation
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

    # Test 3: Clear history
    print("\nTest 3: Clear history")
    bot.clear_history()
    history_after_clear = bot.get_history()
    print(f"Messages after clear: {len(history_after_clear)}")
    print(f"Should be 1 (system message only): {'PASS' if len(history_after_clear) == 1 else 'FAIL'}")

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

    print("\n" + "=" * 50)
    print("Implementation complete!" if response1 else "Needs implementation")
