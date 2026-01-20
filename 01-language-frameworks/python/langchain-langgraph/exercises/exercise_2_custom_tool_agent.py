"""
Exercise 2: Build a Custom Tool Agent

Create an agent with domain-specific tools for a customer support scenario.

Requirements:
1. Create tools for:
   - Looking up order status by order ID
   - Checking product availability
   - Getting return policy information
2. Build a ReAct agent that uses these tools
3. The agent should be helpful and professional

Test scenarios:
- "What's the status of order #12345?"
- "Is the wireless mouse in stock?"
- "What's your return policy?"
- "I want to return order #12345, is it eligible?"

Hints:
- Use @tool decorator with clear docstrings
- Use Pydantic schemas for complex tool inputs
- create_react_agent from langgraph.prebuilt for the agent
- Tools should return helpful, formatted strings
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.tools import tool

load_dotenv()


# Mock data for the exercise
ORDERS_DB = {
    "12345": {
        "status": "shipped",
        "items": ["Wireless Mouse", "USB Cable"],
        "order_date": datetime.now() - timedelta(days=3),
        "tracking": "1Z999AA10123456784"
    },
    "12346": {
        "status": "processing",
        "items": ["Keyboard"],
        "order_date": datetime.now() - timedelta(days=1),
        "tracking": None
    },
    "12347": {
        "status": "delivered",
        "items": ["Monitor Stand"],
        "order_date": datetime.now() - timedelta(days=10),
        "tracking": "1Z999AA10123456785"
    }
}

INVENTORY = {
    "wireless mouse": {"in_stock": True, "quantity": 150, "price": 29.99},
    "keyboard": {"in_stock": True, "quantity": 75, "price": 79.99},
    "monitor stand": {"in_stock": False, "quantity": 0, "price": 49.99},
    "usb cable": {"in_stock": True, "quantity": 500, "price": 9.99},
    "webcam": {"in_stock": True, "quantity": 25, "price": 89.99},
}

RETURN_POLICY = """
Our return policy:
- Items can be returned within 30 days of delivery
- Items must be in original packaging and unused
- Refunds are processed within 5-7 business days
- Free return shipping for defective items
- $5.99 return shipping fee for other returns
"""


# TODO: Implement the tools

# Tool 1: Order Status Lookup
# @tool
# def lookup_order_status(order_id: str) -> str:
#     """Look up the status of an order by order ID."""
#     pass


# Tool 2: Check Product Availability
# class ProductCheckInput(BaseModel):
#     product_name: str = Field(description="Name of the product to check")
#
# @tool(args_schema=ProductCheckInput)
# def check_product_availability(product_name: str) -> str:
#     """Check if a product is available in stock."""
#     pass


# Tool 3: Get Return Policy
# @tool
# def get_return_policy() -> str:
#     """Get information about the return policy."""
#     pass


def create_support_agent():
    """Create a customer support agent with the defined tools.

    Returns:
        A ReAct agent configured with support tools
    """
    # TODO: Implement
    # 1. Collect all tools in a list
    # 2. Initialize ChatOpenAI model
    # 3. Use create_react_agent to build the agent
    # 4. Return the agent
    pass


def handle_customer_query(query: str) -> str:
    """Handle a customer support query.

    Args:
        query: The customer's question or request

    Returns:
        The agent's response
    """
    # TODO: Implement
    # 1. Create the agent
    # 2. Invoke with the query
    # 3. Extract and return the response
    pass


# Test your implementation
if __name__ == "__main__":
    test_queries = [
        "What's the status of order #12345?",
        "Is the wireless mouse in stock?",
        "What's your return policy?",
        "I received order #12347 last week. Can I still return it?",
        "Do you have any webcams available?",
    ]

    print("Testing Customer Support Agent")
    print("=" * 50)

    for query in test_queries:
        print(f"\nCustomer: {query}")
        response = handle_customer_query(query)
        if response:
            print(f"Agent: {response}")
        else:
            print("Agent: [Not implemented yet]")
        print("-" * 50)
