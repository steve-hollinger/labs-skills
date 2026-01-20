"""
Example 4: Conversational Agent with Memory

This example demonstrates how to create an agent that maintains conversation
history and state across multiple interactions using LangGraph's checkpointing.

Key concepts:
- Checkpointing for state persistence
- Thread-based conversation isolation
- Message history management
- Stateful agent interactions
"""

import os
from typing import TypedDict, Annotated
from operator import add
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# Load environment variables
load_dotenv()


# ============================================================================
# State Definition
# ============================================================================

class ConversationState(TypedDict):
    """State for conversational agent.

    Attributes:
        messages: Conversation history (accumulates)
        user_name: Remembered user name
        user_preferences: User preferences learned during conversation
        turn_count: Number of conversation turns
    """
    messages: Annotated[list, add]
    user_name: str | None
    user_preferences: dict
    turn_count: int


# ============================================================================
# Agent Logic
# ============================================================================

def extract_user_info(messages: list) -> dict:
    """Extract user information from messages."""
    info = {"name": None, "preferences": {}}

    for msg in messages:
        content = ""
        if isinstance(msg, HumanMessage):
            content = msg.content.lower()
        elif isinstance(msg, dict) and msg.get("role") == "user":
            content = msg.get("content", "").lower()

        # Simple name extraction
        if "my name is" in content:
            name_start = content.find("my name is") + len("my name is")
            name = content[name_start:].strip().split()[0].strip(".,!?").title()
            info["name"] = name

        if "i'm " in content or "i am " in content:
            for phrase in ["i'm ", "i am "]:
                if phrase in content:
                    idx = content.find(phrase) + len(phrase)
                    name = content[idx:].strip().split()[0].strip(".,!?").title()
                    if name.isalpha() and len(name) > 1:
                        info["name"] = name
                    break

        # Extract preferences
        if "i like" in content:
            pref_start = content.find("i like") + len("i like")
            preference = content[pref_start:].strip().split(".")[0].strip()
            info["preferences"]["likes"] = preference

        if "i prefer" in content:
            pref_start = content.find("i prefer") + len("i prefer")
            preference = content[pref_start:].strip().split(".")[0].strip()
            info["preferences"]["prefers"] = preference

    return info


def generate_response_mock(state: ConversationState) -> str:
    """Generate a response without LLM (mock version)."""
    messages = state["messages"]
    user_name = state.get("user_name")
    turn_count = state.get("turn_count", 0)

    # Get the last user message
    last_user_msg = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_user_msg = msg.content
            break
        elif isinstance(msg, dict) and msg.get("role") == "user":
            last_user_msg = msg.get("content", "")
            break

    # Build response
    greeting = f"Hello {user_name}! " if user_name else "Hello! "

    if turn_count == 0:
        response = f"{greeting}Nice to meet you! How can I help you today?"
    elif "name" in last_user_msg.lower():
        if user_name:
            response = f"Yes, I remember! Your name is {user_name}."
        else:
            response = "I don't think you've told me your name yet."
    elif "remember" in last_user_msg.lower():
        prefs = state.get("user_preferences", {})
        if prefs:
            pref_str = ", ".join(f"{k}: {v}" for k, v in prefs.items())
            response = f"I remember these things about you: {pref_str}"
        else:
            response = "I don't have any specific preferences stored yet."
    elif "bye" in last_user_msg.lower() or "goodbye" in last_user_msg.lower():
        response = f"Goodbye{' ' + user_name if user_name else ''}! It was nice chatting with you."
    else:
        response = f"[Turn {turn_count + 1}] I understand. "
        if user_name:
            response += f"Is there anything else you'd like to discuss, {user_name}?"
        else:
            response += "What else would you like to talk about?"

    return response


def generate_response_llm(state: ConversationState) -> str:
    """Generate a response using LLM."""
    from langchain_openai import ChatOpenAI

    messages = state["messages"]
    user_name = state.get("user_name")
    preferences = state.get("user_preferences", {})

    # Build system message with context
    system_content = "You are a friendly conversational assistant with memory."
    if user_name:
        system_content += f" The user's name is {user_name}."
    if preferences:
        pref_str = ", ".join(f"{k}: {v}" for k, v in preferences.items())
        system_content += f" Known preferences: {pref_str}."

    # Convert to LangChain message format
    lc_messages = [SystemMessage(content=system_content)]
    for msg in messages:
        if isinstance(msg, (HumanMessage, AIMessage, SystemMessage)):
            lc_messages.append(msg)
        elif isinstance(msg, dict):
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    response = model.invoke(lc_messages)

    return response.content


def conversation_node(state: ConversationState) -> dict:
    """Process a conversation turn."""
    # Extract user info from conversation
    user_info = extract_user_info(state["messages"])

    # Update user name if found
    new_name = state.get("user_name")
    if user_info["name"]:
        new_name = user_info["name"]

    # Merge preferences
    new_prefs = {**state.get("user_preferences", {}), **user_info["preferences"]}

    # Generate response
    updated_state = {
        **state,
        "user_name": new_name,
        "user_preferences": new_prefs
    }

    if os.getenv("OPENAI_API_KEY"):
        response = generate_response_llm(updated_state)
    else:
        response = generate_response_mock(updated_state)

    return {
        "messages": [AIMessage(content=response)],
        "user_name": new_name,
        "user_preferences": new_prefs,
        "turn_count": state.get("turn_count", 0) + 1
    }


# ============================================================================
# Graph Construction
# ============================================================================

def create_memory_agent():
    """Create a conversational agent with memory."""
    # Build the graph
    workflow = StateGraph(ConversationState)

    # Add the conversation node
    workflow.add_node("conversation", conversation_node)

    # Connect edges
    workflow.add_edge(START, "conversation")
    workflow.add_edge("conversation", END)

    # Create checkpointer for memory
    memory = MemorySaver()

    # Compile with checkpointer
    return workflow.compile(checkpointer=memory)


# ============================================================================
# Demonstration
# ============================================================================

def chat(agent, message: str, thread_id: str) -> str:
    """Send a message and get a response."""
    config = {"configurable": {"thread_id": thread_id}}

    # Get current state to determine turn count
    try:
        current_state = agent.get_state(config)
        turn_count = current_state.values.get("turn_count", 0) if current_state.values else 0
    except Exception:
        turn_count = 0

    # Invoke with the new message
    result = agent.invoke(
        {
            "messages": [HumanMessage(content=message)],
            "user_name": None,
            "user_preferences": {},
            "turn_count": turn_count
        },
        config
    )

    # Get the last AI message
    messages = result.get("messages", [])
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            return msg.content
        elif isinstance(msg, dict) and msg.get("role") == "assistant":
            return msg.get("content", "")

    return "[No response]"


def main():
    """Run the memory agent examples."""
    print("=" * 60)
    print("Example 4: Conversational Agent with Memory")
    print("=" * 60)

    if not os.getenv("OPENAI_API_KEY"):
        print("\nNote: OPENAI_API_KEY not set. Using mock responses.")

    agent = create_memory_agent()

    # Demonstrate conversation with memory
    print("\n--- Conversation with User Alice (thread: alice-session) ---")
    thread1 = "alice-session"

    conversations = [
        "Hello! My name is Alice.",
        "I like programming and coffee.",
        "What's my name?",
        "What do you remember about me?",
        "Goodbye!"
    ]

    for msg in conversations:
        print(f"\nUser: {msg}")
        response = chat(agent, msg, thread1)
        print(f"Agent: {response}")

    # Demonstrate separate thread (different user)
    print("\n\n--- Separate Conversation with User Bob (thread: bob-session) ---")
    thread2 = "bob-session"

    bob_conversations = [
        "Hi there! I'm Bob.",
        "I prefer Python over JavaScript.",
        "What's my name?",
    ]

    for msg in bob_conversations:
        print(f"\nUser: {msg}")
        response = chat(agent, msg, thread2)
        print(f"Agent: {response}")

    # Return to Alice's thread - should remember her
    print("\n\n--- Returning to Alice's conversation (thread: alice-session) ---")

    print(f"\nUser: Hi again! Do you remember me?")
    response = chat(agent, "Hi again! Do you remember me?", thread1)
    print(f"Agent: {response}")

    # Show state inspection
    print("\n\n--- State Inspection ---")
    config1 = {"configurable": {"thread_id": thread1}}
    state1 = agent.get_state(config1)
    print(f"\nAlice's session state:")
    print(f"  - User name: {state1.values.get('user_name')}")
    print(f"  - Preferences: {state1.values.get('user_preferences')}")
    print(f"  - Turn count: {state1.values.get('turn_count')}")
    print(f"  - Message count: {len(state1.values.get('messages', []))}")

    config2 = {"configurable": {"thread_id": thread2}}
    state2 = agent.get_state(config2)
    print(f"\nBob's session state:")
    print(f"  - User name: {state2.values.get('user_name')}")
    print(f"  - Preferences: {state2.values.get('user_preferences')}")
    print(f"  - Turn count: {state2.values.get('turn_count')}")
    print(f"  - Message count: {len(state2.values.get('messages', []))}")

    print("\n" + "=" * 60)
    print("Key Takeaways:")
    print("1. MemorySaver provides in-memory checkpointing")
    print("2. thread_id isolates conversations between users")
    print("3. State persists across multiple invoke() calls")
    print("4. get_state() allows inspection of conversation state")
    print("5. Memory enables context-aware responses")
    print("=" * 60)


if __name__ == "__main__":
    main()
