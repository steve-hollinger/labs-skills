"""Exercise 3: Implement a Shopping Cart.

In this exercise, you will build a shopping cart system using Redis
hashes with automatic expiration.

Requirements:
1. Create a ShoppingCart class with:
   - add_item(user_id, product_id, quantity, price) - add/update item
   - remove_item(user_id, product_id) -> bool
   - get_item(user_id, product_id) -> CartItem | None
   - get_cart(user_id) -> list[CartItem]
   - update_quantity(user_id, product_id, quantity) -> bool
   - clear_cart(user_id) -> bool
   - get_total(user_id) -> float
   - get_item_count(user_id) -> int

2. Each cart should expire after a configurable time (default 24 hours)

3. Cart items should be stored in a hash with fields:
   - {product_id}:quantity
   - {product_id}:price
   - {product_id}:name (optional)

Run with: python exercises/exercise_3.py
Test with: pytest tests/test_exercises.py -k exercise_3
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List

import redis


@dataclass
class CartItem:
    """A single cart item."""

    product_id: str
    name: str
    quantity: int
    price: float

    @property
    def total(self) -> float:
        """Calculate item total."""
        return self.quantity * self.price


class ShoppingCart:
    """Shopping cart using Redis hashes.

    TODO: Implement this class using HSET, HGET, HGETALL, etc.

    Cart data is stored as a hash with structure:
    cart:{user_id} -> {
        "{product_id}:data": JSON({name, quantity, price})
    }
    """

    def __init__(
        self,
        client: redis.Redis[str],
        cart_ttl: int = 86400,  # 24 hours
        prefix: str = "cart",
    ) -> None:
        """Initialize shopping cart.

        TODO:
        1. Store client, cart_ttl, and prefix
        """
        pass

    def _cart_key(self, user_id: str) -> str:
        """Create cart key for user.

        TODO: Return "{prefix}:{user_id}"
        """
        pass

    def _item_field(self, product_id: str) -> str:
        """Create field name for product.

        TODO: Return "{product_id}:data"
        """
        pass

    def add_item(
        self,
        user_id: str,
        product_id: str,
        name: str,
        quantity: int,
        price: float,
    ) -> None:
        """Add or update an item in the cart.

        TODO:
        1. Create item data as JSON
        2. HSET the item
        3. Reset TTL on the cart
        """
        pass

    def remove_item(self, user_id: str, product_id: str) -> bool:
        """Remove an item from the cart.

        TODO: Use HDEL
        """
        pass

    def get_item(self, user_id: str, product_id: str) -> CartItem | None:
        """Get a single item from the cart.

        TODO:
        1. HGET the item field
        2. Deserialize and return CartItem
        """
        pass

    def get_cart(self, user_id: str) -> List[CartItem]:
        """Get all items in the cart.

        TODO:
        1. HGETALL
        2. Parse each field
        3. Return list of CartItem
        """
        pass

    def update_quantity(
        self,
        user_id: str,
        product_id: str,
        quantity: int,
    ) -> bool:
        """Update item quantity.

        TODO:
        1. Get existing item
        2. Update quantity
        3. Save back
        4. If quantity <= 0, remove item
        """
        pass

    def clear_cart(self, user_id: str) -> bool:
        """Clear all items from cart.

        TODO: DELETE the cart key
        """
        pass

    def get_total(self, user_id: str) -> float:
        """Get cart total.

        TODO: Sum of all item totals
        """
        pass

    def get_item_count(self, user_id: str) -> int:
        """Get total number of items (sum of quantities).

        TODO: Sum all quantities
        """
        pass


def main() -> None:
    """Demonstrate the shopping cart."""
    print("Exercise 3: Shopping Cart")
    print("=" * 40)

    # TODO: Implement the demonstration
    #
    # 1. Connect to Redis
    # 2. Create a ShoppingCart
    # 3. Add items for a user:
    #    - "prod-1": "Widget" x 2 @ $9.99
    #    - "prod-2": "Gadget" x 1 @ $24.99
    #    - "prod-3": "Gizmo" x 3 @ $4.99
    # 4. Display cart contents
    # 5. Show total and item count
    # 6. Update quantity of prod-1 to 5
    # 7. Remove prod-3
    # 8. Show updated cart
    # 9. Clear cart

    print("\nNot implemented yet. See TODO comments.")


if __name__ == "__main__":
    main()
