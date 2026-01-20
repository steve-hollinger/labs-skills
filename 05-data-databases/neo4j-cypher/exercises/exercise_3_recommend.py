"""
Exercise 3: Recommendation Engine

Build a recommendation system using graph traversals.

Tasks:
1. Create a product purchase graph with users and products
2. Write queries to find:
   - Products bought by similar users (collaborative filtering)
   - Product recommendations based on purchase history
   - Users with similar tastes
   - Trending products (most purchased recently)

Instructions:
- Complete the TODO sections below
- Run with: python -m exercises.exercise_3_recommend
- Check your answers against exercises/solutions/solution_3.py
"""

import os
from datetime import datetime, timedelta

from neo4j import GraphDatabase
from rich.console import Console

console = Console()


def get_driver():
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    return GraphDatabase.driver(uri, auth=(user, password))


def setup_data(tx):
    """Create the product purchase graph."""
    # Clean up
    tx.run("MATCH (n:RecUser) DETACH DELETE n")
    tx.run("MATCH (n:RecProduct) DETACH DELETE n")
    tx.run("MATCH (n:RecCategory) DETACH DELETE n")

    # TODO: Create a purchase graph with:
    # - At least 6 users with name property
    # - At least 8 products with name, price, and category properties
    # - At least 3 categories
    #
    # Create relationships:
    # - PURCHASED (user to product) with 'date' and 'rating' properties
    # - IN_CATEGORY (product to category)
    #
    # Design the data so that:
    # - Some users have similar purchase patterns
    # - Products have various ratings
    # - Purchases span different dates

    pass  # Remove this and add your code


def task1_collaborative_filter(tx, user_name: str, limit: int = 5) -> list[dict]:
    """
    Task 1: Find products bought by users with similar tastes.

    Find users who bought the same products as the given user,
    then find OTHER products those similar users bought.

    Args:
        user_name: Name of the user to get recommendations for
        limit: Maximum number of recommendations

    Returns:
        List of dicts with 'product', 'buyerCount', 'avgRating'
    """
    # TODO: Write a collaborative filtering query:
    # 1. Find products the user has purchased
    # 2. Find other users who purchased those same products
    # 3. Find products those users purchased that the original user hasn't
    # 4. Rank by how many similar users purchased each product
    #
    # Hint: Use pattern like:
    # MATCH (user)-[:PURCHASED]->(product)<-[:PURCHASED]-(similarUser)
    # MATCH (similarUser)-[:PURCHASED]->(recommendation)
    # WHERE NOT (user)-[:PURCHASED]->(recommendation)

    query = """
    // TODO: Your query here
    RETURN '' AS product, 0 AS buyerCount, 0.0 AS avgRating
    """

    result = tx.run(query, user_name=user_name, limit=limit)
    return [
        {"product": r["product"], "buyerCount": r["buyerCount"], "avgRating": r["avgRating"]}
        for r in result
    ]


def task2_category_recommendations(tx, user_name: str, limit: int = 5) -> list[dict]:
    """
    Task 2: Recommend products from categories the user likes.

    Find the user's favorite categories (most purchases) and recommend
    highly-rated products from those categories that the user hasn't bought.

    Args:
        user_name: Name of the user
        limit: Maximum recommendations

    Returns:
        List of dicts with 'product', 'category', 'avgRating'
    """
    # TODO: Write a category-based recommendation query:
    # 1. Find categories the user has purchased from most
    # 2. Find highly-rated products in those categories
    # 3. Exclude products the user has already purchased
    # 4. Order by rating

    query = """
    // TODO: Your query here
    RETURN '' AS product, '' AS category, 0.0 AS avgRating
    """

    result = tx.run(query, user_name=user_name, limit=limit)
    return [
        {"product": r["product"], "category": r["category"], "avgRating": r["avgRating"]}
        for r in result
    ]


def task3_similar_users(tx, user_name: str, limit: int = 3) -> list[dict]:
    """
    Task 3: Find users with similar purchase patterns.

    Calculate similarity based on number of products purchased in common.

    Args:
        user_name: Name of the user
        limit: Maximum similar users to return

    Returns:
        List of dicts with 'user', 'commonProducts', 'similarity' score
    """
    # TODO: Write a similarity query:
    # 1. Find products the user has purchased
    # 2. Find other users who purchased the same products
    # 3. Count common products as a similarity measure
    # 4. Could also use Jaccard similarity: common / (user_products + other_products - common)

    query = """
    // TODO: Your query here
    RETURN '' AS user, 0 AS commonProducts, 0.0 AS similarity
    """

    result = tx.run(query, user_name=user_name, limit=limit)
    return [
        {
            "user": r["user"],
            "commonProducts": r["commonProducts"],
            "similarity": r["similarity"],
        }
        for r in result
    ]


def task4_trending_products(tx, days: int = 30, limit: int = 5) -> list[dict]:
    """
    Task 4: Find trending products (most purchased recently).

    Args:
        days: Number of days to look back
        limit: Maximum products to return

    Returns:
        List of dicts with 'product', 'purchases', 'avgRating'
    """
    # TODO: Write a trending products query:
    # 1. Find products purchased within the last N days
    # 2. Count purchases per product
    # 3. Include average rating
    # 4. Order by purchase count
    #
    # Hint: Use datetime() and duration to filter by date
    # WHERE r.date > datetime() - duration({days: $days})

    query = """
    // TODO: Your query here
    RETURN '' AS product, 0 AS purchases, 0.0 AS avgRating
    """

    result = tx.run(query, days=days, limit=limit)
    return [
        {"product": r["product"], "purchases": r["purchases"], "avgRating": r["avgRating"]}
        for r in result
    ]


def main():
    console.print("[bold]Exercise 3: Recommendation Engine[/bold]\n")

    driver = get_driver()

    try:
        driver.verify_connectivity()

        with driver.session() as session:
            # Setup data
            session.execute_write(setup_data)

            # Run tasks
            console.print("[cyan]Task 1: Collaborative Filtering[/cyan]")
            recs = session.execute_read(task1_collaborative_filter, "Alice")
            for r in recs:
                console.print(
                    f"  {r['product']}: {r['buyerCount']} similar users, {r['avgRating']:.1f} rating"
                )

            console.print("\n[cyan]Task 2: Category-Based Recommendations[/cyan]")
            recs = session.execute_read(task2_category_recommendations, "Alice")
            for r in recs:
                console.print(f"  {r['product']} ({r['category']}): {r['avgRating']:.1f} rating")

            console.print("\n[cyan]Task 3: Similar Users[/cyan]")
            similar = session.execute_read(task3_similar_users, "Alice")
            for s in similar:
                console.print(
                    f"  {s['user']}: {s['commonProducts']} common, {s['similarity']:.2f} similarity"
                )

            console.print("\n[cyan]Task 4: Trending Products[/cyan]")
            trending = session.execute_read(task4_trending_products, 30)
            for t in trending:
                console.print(
                    f"  {t['product']}: {t['purchases']} purchases, {t['avgRating']:.1f} rating"
                )

            # Cleanup
            session.execute_write(lambda tx: tx.run("MATCH (n:RecUser) DETACH DELETE n"))
            session.execute_write(lambda tx: tx.run("MATCH (n:RecProduct) DETACH DELETE n"))
            session.execute_write(lambda tx: tx.run("MATCH (n:RecCategory) DETACH DELETE n"))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise

    finally:
        driver.close()


if __name__ == "__main__":
    main()
