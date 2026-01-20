"""
Solution 2: Custom Tool Agent for Customer Support

This solution demonstrates how to create a customer support agent
with domain-specific tools using LangChain and LangGraph.
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

load_dotenv()


# Mock data
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


# Tool implementations

@tool
def lookup_order_status(order_id: str) -> str:
    """Look up the status of an order by order ID.

    Use this tool when a customer asks about their order status,
    shipping information, or tracking details.

    Args:
        order_id: The order ID to look up (e.g., "12345")

    Returns:
        Order status information including items, status, and tracking
    """
    # Clean the order ID
    clean_id = order_id.strip().replace("#", "").replace("order", "").strip()

    if clean_id not in ORDERS_DB:
        return f"Order #{clean_id} not found. Please verify the order number."

    order = ORDERS_DB[clean_id]
    status = order["status"]
    items = ", ".join(order["items"])
    order_date = order["order_date"].strftime("%Y-%m-%d")

    response = f"""Order #{clean_id} Details:
- Status: {status.upper()}
- Items: {items}
- Order Date: {order_date}"""

    if order["tracking"]:
        response += f"\n- Tracking Number: {order['tracking']}"

    if status == "shipped":
        response += "\n- Expected delivery: 2-3 business days"
    elif status == "delivered":
        delivery_date = order["order_date"] + timedelta(days=5)
        response += f"\n- Delivered on: {delivery_date.strftime('%Y-%m-%d')}"

    return response


class ProductCheckInput(BaseModel):
    """Input schema for product availability check."""
    product_name: str = Field(description="Name of the product to check availability for")


@tool(args_schema=ProductCheckInput)
def check_product_availability(product_name: str) -> str:
    """Check if a product is available in stock.

    Use this tool when a customer asks about product availability,
    stock levels, or pricing information.

    Args:
        product_name: Name of the product to check

    Returns:
        Availability status, quantity, and price information
    """
    # Normalize product name
    product_lower = product_name.lower().strip()

    # Try exact match first
    if product_lower in INVENTORY:
        product = INVENTORY[product_lower]
        if product["in_stock"]:
            return (
                f"{product_name.title()} is IN STOCK!\n"
                f"- Available quantity: {product['quantity']} units\n"
                f"- Price: ${product['price']:.2f}"
            )
        else:
            return (
                f"{product_name.title()} is currently OUT OF STOCK.\n"
                f"- Price: ${product['price']:.2f}\n"
                f"- Would you like to be notified when it's back in stock?"
            )

    # Try partial match
    matches = [name for name in INVENTORY.keys() if product_lower in name or name in product_lower]
    if matches:
        product_key = matches[0]
        product = INVENTORY[product_key]
        stock_status = "IN STOCK" if product["in_stock"] else "OUT OF STOCK"
        return (
            f"Did you mean '{product_key.title()}'?\n"
            f"- Status: {stock_status}\n"
            f"- Price: ${product['price']:.2f}"
        )

    available = ", ".join(name.title() for name in INVENTORY.keys())
    return f"Product '{product_name}' not found. Available products: {available}"


@tool
def get_return_policy() -> str:
    """Get information about the return policy.

    Use this tool when a customer asks about returns, refunds,
    or the return process.

    Returns:
        Complete return policy information
    """
    return RETURN_POLICY


@tool
def check_return_eligibility(order_id: str) -> str:
    """Check if an order is eligible for return.

    Use this tool when a customer wants to know if they can return
    a specific order.

    Args:
        order_id: The order ID to check for return eligibility

    Returns:
        Return eligibility status and instructions
    """
    clean_id = order_id.strip().replace("#", "").replace("order", "").strip()

    if clean_id not in ORDERS_DB:
        return f"Order #{clean_id} not found. Please verify the order number."

    order = ORDERS_DB[clean_id]

    if order["status"] != "delivered":
        return (
            f"Order #{clean_id} has not been delivered yet (Status: {order['status']}).\n"
            "Returns can only be initiated after delivery."
        )

    # Calculate days since delivery (assuming 5 days after order for delivery)
    delivery_date = order["order_date"] + timedelta(days=5)
    days_since_delivery = (datetime.now() - delivery_date).days

    if days_since_delivery <= 30:
        return (
            f"Order #{clean_id} IS ELIGIBLE for return!\n"
            f"- Delivered: {delivery_date.strftime('%Y-%m-%d')} ({days_since_delivery} days ago)\n"
            f"- Return window: {30 - days_since_delivery} days remaining\n"
            f"- Items: {', '.join(order['items'])}\n\n"
            "To initiate a return, please contact support with your order number."
        )
    else:
        return (
            f"Order #{clean_id} is NOT ELIGIBLE for return.\n"
            f"- Delivered: {delivery_date.strftime('%Y-%m-%d')} ({days_since_delivery} days ago)\n"
            f"- Return window expired {days_since_delivery - 30} days ago.\n\n"
            "Our return policy allows returns within 30 days of delivery."
        )


def create_support_agent():
    """Create a customer support agent with the defined tools.

    Returns:
        A ReAct agent configured with support tools
    """
    tools = [
        lookup_order_status,
        check_product_availability,
        get_return_policy,
        check_return_eligibility
    ]

    if not os.getenv("OPENAI_API_KEY"):
        print("Note: OPENAI_API_KEY not set. Using mock agent.")
        return create_mock_agent(tools)

    from langchain_openai import ChatOpenAI
    from langgraph.prebuilt import create_react_agent

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # System message for the agent
    system_message = """You are a helpful customer support agent for an e-commerce store.
    Be friendly, professional, and thorough in your responses.
    Always use the available tools to look up accurate information.
    If you need to check multiple things (like order status AND return eligibility),
    use all relevant tools to provide a complete answer."""

    agent = create_react_agent(model, tools, state_modifier=system_message)

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

        response = "[Mock Agent Response]\n"

        # Simulate tool usage based on keywords
        if "order" in user_message.lower() and "#" in user_message:
            # Extract order ID
            import re
            match = re.search(r"#?(\d{5})", user_message)
            if match:
                order_id = match.group(1)
                response += lookup_order_status.invoke({"order_id": order_id})

                if "return" in user_message.lower():
                    response += "\n\n" + check_return_eligibility.invoke({"order_id": order_id})

        elif "stock" in user_message.lower() or "available" in user_message.lower():
            # Try to extract product name
            for product in INVENTORY.keys():
                if product in user_message.lower():
                    response += check_product_availability.invoke({"product_name": product})
                    break
            else:
                response += "Please specify which product you'd like to check."

        elif "return policy" in user_message.lower():
            response += get_return_policy.invoke({})

        else:
            response += "I can help you with:\n- Order status (provide order #)\n- Product availability\n- Return policy"

        return {"messages": [{"role": "assistant", "content": response}]}

    return RunnableLambda(mock_agent_response)


def handle_customer_query(query: str) -> str:
    """Handle a customer support query.

    Args:
        query: The customer's question or request

    Returns:
        The agent's response
    """
    agent = create_support_agent()
    result = agent.invoke({"messages": [("user", query)]})

    messages = result.get("messages", [])
    if messages:
        final_message = messages[-1]
        if hasattr(final_message, "content"):
            return final_message.content
        elif isinstance(final_message, dict):
            return final_message.get("content", str(final_message))
    return "[No response]"


# Test the implementation
if __name__ == "__main__":
    test_queries = [
        "What's the status of order #12345?",
        "Is the wireless mouse in stock?",
        "What's your return policy?",
        "I received order #12347 last week. Can I still return it?",
        "Do you have any webcams available?",
        "Can I return order #12345?",
    ]

    print("Testing Customer Support Agent")
    print("=" * 60)

    for query in test_queries:
        print(f"\nCustomer: {query}")
        print("-" * 40)
        response = handle_customer_query(query)
        print(f"Agent: {response}")
        print("=" * 60)
