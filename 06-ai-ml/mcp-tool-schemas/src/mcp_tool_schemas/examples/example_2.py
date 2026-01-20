"""Example 2: Complex Schemas

This example demonstrates advanced schema features including:
- Nested objects
- Arrays with item schemas
- Conditional validation
- Complex constraints
"""

import json

from mcp_tool_schemas import (
    ToolDefinition,
    ToolParameter,
    ValidationError,
    validate_input,
)
from mcp_tool_schemas.validation import check_tool_definition, generate_example_input


def main() -> None:
    """Run the complex schemas example."""
    print("Example 2: Complex Schemas")
    print("=" * 60)

    # Tool with nested object parameters
    print("\n1. Nested Object Schema")
    print("-" * 40)

    create_order_tool = ToolDefinition(
        name="create_order",
        description="""Create a new order in the system.

        Creates an order with the specified items and shipping details.
        Validates inventory availability before creating.
        Returns the order ID and estimated delivery date.
        """,
        parameters=[
            ToolParameter(
                name="customer_id",
                type="string",
                description="Customer identifier",
                required=True,
                pattern=r"^CUST-\d{6}$",  # e.g., CUST-123456
            ),
            ToolParameter(
                name="items",
                type="array",
                description="List of items to order",
                required=True,
                min_items=1,
                max_items=50,
                items={
                    "type": "object",
                    "properties": {
                        "product_id": {
                            "type": "string",
                            "description": "Product identifier",
                            "pattern": r"^PROD-\d{5}$",
                        },
                        "quantity": {
                            "type": "integer",
                            "description": "Number of items",
                            "minimum": 1,
                            "maximum": 100,
                        },
                        "notes": {
                            "type": "string",
                            "description": "Special instructions",
                            "maxLength": 200,
                        },
                    },
                    "required": ["product_id", "quantity"],
                },
            ),
            ToolParameter(
                name="shipping",
                type="object",
                description="Shipping information",
                required=True,
                properties={
                    "address": {
                        "type": "object",
                        "description": "Delivery address",
                        "properties": {
                            "street": {"type": "string"},
                            "city": {"type": "string"},
                            "state": {"type": "string"},
                            "zip": {"type": "string", "pattern": r"^\d{5}(-\d{4})?$"},
                            "country": {"type": "string", "default": "US"},
                        },
                        "required": ["street", "city", "state", "zip"],
                    },
                    "method": {
                        "type": "string",
                        "description": "Shipping method",
                        "enum": ["standard", "express", "overnight"],
                        "default": "standard",
                    },
                    "signature_required": {
                        "type": "boolean",
                        "description": "Require signature on delivery",
                        "default": False,
                    },
                },
                additional_properties=False,
            ),
            ToolParameter(
                name="payment",
                type="object",
                description="Payment information",
                required=True,
                properties={
                    "method": {
                        "type": "string",
                        "enum": ["credit_card", "debit_card", "paypal", "invoice"],
                    },
                    "card_last_four": {
                        "type": "string",
                        "description": "Last 4 digits of card (if card payment)",
                        "pattern": r"^\d{4}$",
                    },
                    "billing_same_as_shipping": {
                        "type": "boolean",
                        "default": True,
                    },
                },
            ),
            ToolParameter(
                name="gift_options",
                type="object",
                description="Optional gift wrapping and message",
                required=False,
                properties={
                    "wrap": {"type": "boolean", "default": False},
                    "message": {"type": "string", "maxLength": 500},
                    "recipient_name": {"type": "string"},
                },
            ),
        ],
    )

    schema = create_order_tool.to_json_schema()
    print(json.dumps(schema, indent=2))

    # Validate a complex input
    print("\n2. Validating Complex Input")
    print("-" * 40)

    valid_order = {
        "customer_id": "CUST-123456",
        "items": [
            {"product_id": "PROD-00001", "quantity": 2},
            {"product_id": "PROD-00002", "quantity": 1, "notes": "Gift wrap please"},
        ],
        "shipping": {
            "address": {
                "street": "123 Main St",
                "city": "San Francisco",
                "state": "CA",
                "zip": "94102",
            },
            "method": "express",
        },
        "payment": {
            "method": "credit_card",
            "card_last_four": "4242",
        },
    }

    print(f"Input:\n{json.dumps(valid_order, indent=2)}")
    try:
        result = validate_input(create_order_tool, valid_order)
        print("\nValid! Validated input (with defaults):")
        print(json.dumps(result, indent=2))
    except ValidationError as e:
        print(f"\nInvalid: {e}")

    # Invalid nested input
    print("\n3. Invalid Nested Input")
    print("-" * 40)

    invalid_order = {
        "customer_id": "INVALID",  # Wrong pattern
        "items": [
            {"product_id": "PROD-00001", "quantity": 200},  # quantity too high
        ],
        "shipping": {
            "address": {
                "street": "123 Main St",
                # Missing required fields
            },
        },
        "payment": {
            "method": "bitcoin",  # Invalid enum
        },
    }

    print(f"Input:\n{json.dumps(invalid_order, indent=2)}")
    try:
        result = validate_input(create_order_tool, invalid_order)
        print("Valid!")
    except ValidationError as e:
        print(f"\nValidation errors:")
        for error in e.errors:
            print(f"  - {error}")

    # Tool with array of strings
    print("\n4. Array Parameters")
    print("-" * 40)

    bulk_action_tool = ToolDefinition(
        name="bulk_update_tags",
        description="""Update tags for multiple items at once.

        Efficiently adds or removes tags from multiple items.
        Supports both adding and removing tags in a single operation.
        """,
        parameters=[
            ToolParameter(
                name="item_ids",
                type="array",
                description="IDs of items to update",
                required=True,
                min_items=1,
                max_items=100,
                items={"type": "string", "pattern": r"^ITEM-\d+$"},
                unique_items=True,
            ),
            ToolParameter(
                name="add_tags",
                type="array",
                description="Tags to add",
                items={"type": "string", "minLength": 1, "maxLength": 50},
                default=[],
            ),
            ToolParameter(
                name="remove_tags",
                type="array",
                description="Tags to remove",
                items={"type": "string"},
                default=[],
            ),
        ],
    )

    print(json.dumps(bulk_action_tool.to_json_schema(), indent=2))

    # Check tool definitions
    print("\n5. Tool Definition Lint Check")
    print("-" * 40)

    # A tool with issues
    problematic_tool = ToolDefinition(
        name="123_bad_name",  # Starts with number
        description="Does stuff",  # Too vague
        parameters=[
            ToolParameter(
                name="input",
                type="string",
                description="",  # Empty description
                required=True,
            ),
            ToolParameter(
                name="count",
                type="integer",
                description="A number",  # No constraints
            ),
        ],
    )

    issues = check_tool_definition(problematic_tool)
    print("Issues found in problematic tool:")
    for issue in issues:
        print(f"  - {issue}")

    # Generate example input
    print("\n6. Generate Example Input")
    print("-" * 40)

    example = generate_example_input(create_order_tool)
    print("Generated example input:")
    print(json.dumps(example, indent=2, default=str))

    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
