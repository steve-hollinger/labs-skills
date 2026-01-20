"""Example 2: Caching Patterns.

This example demonstrates common caching patterns including cache-aside,
write-through, and cache invalidation.

Learning objectives:
- Implement cache-aside pattern
- Handle cache invalidation
- Prevent cache stampede with locking
- Use cache warming

Prerequisites:
- Valkey running on localhost:6379
- Start with: make infra-up (from repository root)
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass
from typing import Any

import redis


# Simulated database
@dataclass
class Product:
    id: str
    name: str
    price: float
    stock: int


class SimulatedDatabase:
    """Simulates a slow database."""

    def __init__(self) -> None:
        self._products: dict[str, Product] = {
            "prod-1": Product("prod-1", "Widget", 29.99, 100),
            "prod-2": Product("prod-2", "Gadget", 49.99, 50),
            "prod-3": Product("prod-3", "Gizmo", 19.99, 200),
        }
        self.query_count = 0

    def get_product(self, product_id: str) -> Product | None:
        """Simulate slow database query."""
        time.sleep(0.1)  # Simulate 100ms latency
        self.query_count += 1
        return self._products.get(product_id)

    def update_product(self, product: Product) -> None:
        """Update a product."""
        time.sleep(0.05)  # Simulate 50ms latency
        self._products[product.id] = product


def main() -> None:
    print("=" * 60)
    print("Example 2: Caching Patterns")
    print("=" * 60)

    try:
        client: redis.Redis[str] = redis.Redis(
            host="localhost",
            port=6379,
            decode_responses=True,
        )
        client.ping()
        print("\n[OK] Connected to Valkey")
    except redis.ConnectionError as e:
        print(f"\n[ERROR] Could not connect: {e}")
        print("\nMake sure Valkey is running:")
        print("  cd ../../.. && make infra-up")
        return

    # Clean up
    for key in client.scan_iter(match="example2:*"):
        client.delete(key)

    db = SimulatedDatabase()

    # Part 1: Cache-Aside Pattern
    print("\n" + "-" * 40)
    print("PART 1: Cache-Aside Pattern")
    print("-" * 40)

    def get_product_cached(product_id: str) -> dict[str, Any] | None:
        """Get product with cache-aside pattern."""
        cache_key = f"example2:product:{product_id}"

        # Try cache first
        cached = client.get(cache_key)
        if cached:
            print(f"    Cache HIT for {product_id}")
            return json.loads(cached)

        # Cache miss - fetch from database
        print(f"    Cache MISS for {product_id}")
        product = db.get_product(product_id)
        if product is None:
            return None

        # Cache the result
        product_dict = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "stock": product.stock,
        }
        client.setex(cache_key, 3600, json.dumps(product_dict))

        return product_dict

    print("\n  First request (cache miss):")
    start = time.time()
    product = get_product_cached("prod-1")
    first_time = time.time() - start
    print(f"    Result: {product}")
    print(f"    Time: {first_time*1000:.2f}ms")

    print("\n  Second request (cache hit):")
    start = time.time()
    product = get_product_cached("prod-1")
    second_time = time.time() - start
    print(f"    Result: {product}")
    print(f"    Time: {second_time*1000:.2f}ms")
    print(f"    Speedup: {first_time/second_time:.1f}x faster")

    # Part 2: Cache Invalidation
    print("\n" + "-" * 40)
    print("PART 2: Cache Invalidation")
    print("-" * 40)

    def update_product(product_id: str, new_price: float) -> None:
        """Update product and invalidate cache."""
        # Update database
        product = db.get_product(product_id)
        if product:
            product.price = new_price
            db.update_product(product)

            # Invalidate cache
            cache_key = f"example2:product:{product_id}"
            client.delete(cache_key)
            print(f"    Updated {product_id} and invalidated cache")

    print("\n  Before update:")
    product = get_product_cached("prod-1")
    print(f"    Price: ${product['price'] if product else 'N/A'}")

    print("\n  Updating price...")
    update_product("prod-1", 34.99)

    print("\n  After update (cache miss, fresh data):")
    product = get_product_cached("prod-1")
    print(f"    Price: ${product['price'] if product else 'N/A'}")

    # Part 3: Write-Through Pattern
    print("\n" + "-" * 40)
    print("PART 3: Write-Through Pattern")
    print("-" * 40)

    def update_product_write_through(product_id: str, new_stock: int) -> None:
        """Update with write-through: database first, then cache."""
        # Update database
        product = db.get_product(product_id)
        if product:
            product.stock = new_stock
            db.update_product(product)

            # Update cache (not invalidate)
            cache_key = f"example2:product:{product_id}"
            product_dict = {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "stock": product.stock,
            }
            client.setex(cache_key, 3600, json.dumps(product_dict))
            print(f"    Updated DB and cache for {product_id}")

    print("\n  Write-through update (stock: 150):")
    update_product_write_through("prod-2", 150)

    print("\n  Read after write (immediate consistency):")
    product = get_product_cached("prod-2")
    print(f"    Stock: {product['stock'] if product else 'N/A'}")

    # Part 4: Cache Stampede Prevention
    print("\n" + "-" * 40)
    print("PART 4: Cache Stampede Prevention")
    print("-" * 40)

    def get_product_with_lock(product_id: str) -> dict[str, Any] | None:
        """Get product with lock to prevent stampede."""
        cache_key = f"example2:product:{product_id}"
        lock_key = f"example2:lock:{product_id}"

        # Try cache first
        cached = client.get(cache_key)
        if cached:
            return json.loads(cached)

        # Try to acquire lock
        lock_id = str(uuid.uuid4())
        if client.set(lock_key, lock_id, nx=True, ex=10):
            try:
                # Double-check cache
                cached = client.get(cache_key)
                if cached:
                    return json.loads(cached)

                # Fetch and cache
                print(f"    [{lock_id[:8]}] Acquired lock, fetching from DB")
                product = db.get_product(product_id)
                if product is None:
                    return None

                product_dict = {
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "stock": product.stock,
                }
                client.setex(cache_key, 3600, json.dumps(product_dict))
                return product_dict
            finally:
                # Release lock
                client.delete(lock_key)
                print(f"    [{lock_id[:8]}] Released lock")
        else:
            # Wait for lock holder
            print(f"    Waiting for lock holder...")
            for _ in range(100):
                time.sleep(0.01)
                cached = client.get(cache_key)
                if cached:
                    return json.loads(cached)
            return None

    # Clear cache to demonstrate
    client.delete("example2:product:prod-3")

    print("\n  Simulating concurrent requests (without stampede):")
    import threading

    results: list[dict[str, Any] | None] = []

    def fetch_product() -> None:
        result = get_product_with_lock("prod-3")
        results.append(result)

    threads = [threading.Thread(target=fetch_product) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"\n    All {len(results)} requests completed")
    print(f"    Database queries: {db.query_count} (should be minimal)")

    # Part 5: Cache Warming
    print("\n" + "-" * 40)
    print("PART 5: Cache Warming")
    print("-" * 40)

    def warm_cache(product_ids: list[str]) -> int:
        """Pre-populate cache with frequently accessed items."""
        warmed = 0
        pipe = client.pipeline()

        for product_id in product_ids:
            product = db.get_product(product_id)
            if product:
                cache_key = f"example2:product:{product_id}"
                product_dict = {
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "stock": product.stock,
                }
                pipe.setex(cache_key, 3600, json.dumps(product_dict))
                warmed += 1

        pipe.execute()
        return warmed

    # Clear cache
    for key in client.scan_iter(match="example2:product:*"):
        client.delete(key)

    print("\n  Warming cache with all products:")
    start = time.time()
    warmed = warm_cache(["prod-1", "prod-2", "prod-3"])
    warm_time = time.time() - start
    print(f"    Warmed {warmed} products in {warm_time*1000:.2f}ms")

    print("\n  Verifying cache:")
    for pid in ["prod-1", "prod-2", "prod-3"]:
        cached = client.get(f"example2:product:{pid}")
        status = "CACHED" if cached else "MISSING"
        print(f"    {pid}: {status}")

    # Cleanup
    print("\n" + "-" * 40)
    print("Cleanup")
    print("-" * 40)
    deleted = 0
    for key in client.scan_iter(match="example2:*"):
        client.delete(key)
        deleted += 1
    print(f"  Deleted {deleted} example keys")

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
