"""
Example 2: Tool-Using Agent

This example demonstrates how to create agents that use tools to accomplish tasks.
The agent decides when and how to use tools based on the user's request.

Key concepts:
- Defining tools with @tool decorator
- Tool schemas with Pydantic
- Creating ReAct agents with LangGraph
- Tool execution and response handling
"""

import os
import math
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()


# ============================================================================
# Tool Definitions
# ============================================================================

@tool
def calculator(expression: str) -> str:
    """
    Calculate a mathematical expression.

    Args:
        expression: A mathematical expression to evaluate (e.g., "2 + 2", "sqrt(16)")

    Returns:
        The result of the calculation as a string.
    """
    # Safe evaluation with math functions
    allowed_names = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        "pow": pow,
        "abs": abs,
        "round": round,
        "pi": math.pi,
        "e": math.e,
    }
    try:
        # Replace common math notation
        expr = expression.replace("^", "**")
        result = eval(expr, {"__builtins__": {}}, allowed_names)
        return f"Result: {result}"
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"


@tool
def get_current_time() -> str:
    """
    Get the current date and time.

    Returns:
        The current date and time in a readable format.
    """
    now = datetime.now()
    return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"


class WeatherInput(BaseModel):
    """Input schema for weather tool."""
    city: str = Field(description="The city to get weather for")
    unit: str = Field(default="celsius", description="Temperature unit: 'celsius' or 'fahrenheit'")


@tool(args_schema=WeatherInput)
def get_weather(city: str, unit: str = "celsius") -> str:
    """
    Get the current weather for a city.

    This is a mock implementation for demonstration purposes.

    Args:
        city: The city to get weather for
        unit: Temperature unit ('celsius' or 'fahrenheit')

    Returns:
        Weather information for the specified city.
    """
    # Mock weather data
    mock_weather = {
        "new york": {"temp_c": 22, "condition": "Partly cloudy"},
        "london": {"temp_c": 15, "condition": "Rainy"},
        "tokyo": {"temp_c": 28, "condition": "Sunny"},
        "sydney": {"temp_c": 18, "condition": "Clear"},
    }

    city_lower = city.lower()
    if city_lower in mock_weather:
        data = mock_weather[city_lower]
        temp = data["temp_c"]
        if unit.lower() == "fahrenheit":
            temp = temp * 9/5 + 32
            unit_symbol = "F"
        else:
            unit_symbol = "C"
        return f"Weather in {city}: {temp:.1f} degrees {unit_symbol}, {data['condition']}"
    else:
        return f"Weather data not available for {city}. Try: New York, London, Tokyo, or Sydney."


@tool
def search_knowledge_base(query: str) -> str:
    """
    Search a knowledge base for information.

    This is a mock implementation for demonstration purposes.

    Args:
        query: The search query

    Returns:
        Relevant information from the knowledge base.
    """
    # Mock knowledge base
    knowledge = {
        "langchain": "LangChain is a framework for developing applications powered by language models. It provides tools for chains, agents, and memory management.",
        "langgraph": "LangGraph is a library for building stateful, multi-actor applications with LLMs. It extends LangChain with graph-based workflows.",
        "python": "Python is a high-level programming language known for its readability and versatility. It's widely used in AI, web development, and data science.",
        "machine learning": "Machine learning is a subset of AI that enables systems to learn and improve from experience without being explicitly programmed.",
    }

    query_lower = query.lower()
    for key, value in knowledge.items():
        if key in query_lower:
            return f"Knowledge base result: {value}"

    return f"No specific information found for '{query}'. The knowledge base contains information about: {', '.join(knowledge.keys())}"


# ============================================================================
# Agent Creation
# ============================================================================

def create_tool_agent():
    """Create an agent with access to multiple tools."""
    tools = [calculator, get_current_time, get_weather, search_knowledge_base]

    if not os.getenv("OPENAI_API_KEY"):
        print("Note: OPENAI_API_KEY not set. Using mock agent.")
        return create_mock_agent(tools)

    from langchain_openai import ChatOpenAI
    from langgraph.prebuilt import create_react_agent

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Create the ReAct agent
    agent = create_react_agent(model, tools)

    return agent


def create_mock_agent(tools: list):
    """Create a mock agent for demonstration."""
    from langchain_core.runnables import RunnableLambda

    def mock_agent_response(input_dict: dict) -> dict:
        messages = input_dict.get("messages", [])
        user_message = ""
        for msg in messages:
            if isinstance(msg, tuple) and msg[0] == "user":
                user_message = msg[1]
            elif isinstance(msg, HumanMessage):
                user_message = msg.content
            elif isinstance(msg, dict) and msg.get("role") == "user":
                user_message = msg.get("content", "")

        # Simulate tool usage based on keywords
        response_content = f"[Mock Agent] Processing: '{user_message}'\n"

        if "calculate" in user_message.lower() or any(c.isdigit() for c in user_message):
            response_content += "\nI would use the calculator tool to help with this math problem."
        if "weather" in user_message.lower():
            response_content += "\nI would use the weather tool to get current conditions."
        if "time" in user_message.lower():
            result = get_current_time.invoke({})
            response_content += f"\nUsing time tool: {result}"
        if "what is" in user_message.lower():
            response_content += "\nI would search the knowledge base for this information."

        return {"messages": [{"role": "assistant", "content": response_content}]}

    return RunnableLambda(mock_agent_response)


# ============================================================================
# Demonstration
# ============================================================================

def run_agent_query(agent, query: str):
    """Run a query through the agent and display results."""
    print(f"\nUser: {query}")
    print("-" * 40)

    result = agent.invoke({"messages": [("user", query)]})

    # Extract the final response
    messages = result.get("messages", [])
    if messages:
        final_message = messages[-1]
        if hasattr(final_message, "content"):
            print(f"Agent: {final_message.content}")
        elif isinstance(final_message, dict):
            print(f"Agent: {final_message.get('content', str(final_message))}")
        else:
            print(f"Agent: {final_message}")


def main():
    """Run the tool agent examples."""
    print("=" * 60)
    print("Example 2: Tool-Using Agent")
    print("=" * 60)

    # Create the agent
    agent = create_tool_agent()

    # Test various queries that require different tools
    queries = [
        "What is the current time?",
        "Calculate the square root of 144 plus 25 times 3",
        "What's the weather like in Tokyo?",
        "What is LangChain and how does it work?",
        "Calculate 15% of 250 and tell me the time",
    ]

    for query in queries:
        run_agent_query(agent, query)
        print()

    print("=" * 60)
    print("Key Takeaways:")
    print("1. Use @tool decorator to define tools with docstrings")
    print("2. Pydantic schemas provide structured tool inputs")
    print("3. create_react_agent builds agents that reason and act")
    print("4. Agents automatically select tools based on the query")
    print("=" * 60)


if __name__ == "__main__":
    main()
