"""
Solution 3: Recommendation Engine

Complete solution for Exercise 3.
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

    # Create categories
    tx.run(
        """
        CREATE (:RecCategory {name: 'Electronics'})
        CREATE (:RecCategory {name: 'Books'})
        CREATE (:RecCategory {name: 'Clothing'})
        """
    )

    # Create products
    tx.run(
        """
        CREATE (:RecProduct {name: 'Laptop', price: 999.99})
        CREATE (:RecProduct {name: 'Smartphone', price: 699.99})
        CREATE (:RecProduct {name: 'Headphones', price: 199.99})
        CREATE (:RecProduct {name: 'Python Book', price: 49.99})
        CREATE (:RecProduct {name: 'Data Science Book', price: 59.99})
        CREATE (:RecProduct {name: 'Fiction Novel', price: 14.99})
        CREATE (:RecProduct {name: 'T-Shirt', price: 29.99})
        CREATE (:RecProduct {name: 'Jeans', price: 79.99})
        """
    )

    # Connect products to categories
    tx.run(
        """
        MATCH (p:RecProduct), (c:RecCategory {name: 'Electronics'})
        WHERE p.name IN ['Laptop', 'Smartphone', 'Headphones']
        CREATE (p)-[:IN_CATEGORY]->(c)
        """
    )
    tx.run(
        """
        MATCH (p:RecProduct), (c:RecCategory {name: 'Books'})
        WHERE p.name IN ['Python Book', 'Data Science Book', 'Fiction Novel']
        CREATE (p)-[:IN_CATEGORY]->(c)
        """
    )
    tx.run(
        """
        MATCH (p:RecProduct), (c:RecCategory {name: 'Clothing'})
        WHERE p.name IN ['T-Shirt', 'Jeans']
        CREATE (p)-[:IN_CATEGORY]->(c)
        """
    )

    # Create users
    tx.run(
        """
        CREATE (:RecUser {name: 'Alice'})
        CREATE (:RecUser {name: 'Bob'})
        CREATE (:RecUser {name: 'Charlie'})
        CREATE (:RecUser {name: 'Diana'})
        CREATE (:RecUser {name: 'Eve'})
        CREATE (:RecUser {name: 'Frank'})
        """
    )

    # Create purchase relationships with dates and ratings
    # Alice buys tech stuff
    tx.run(
        """
        MATCH (u:RecUser {name: 'Alice'}), (p:RecProduct {name: 'Laptop'})
        CREATE (u)-[:PURCHASED {date: datetime() - duration({days: 10}), rating: 5}]->(p)
        """
    )
    tx.run(
        """
        MATCH (u:RecUser {name: 'Alice'}), (p:RecProduct {name: 'Smartphone'})
        CREATE (u)-[:PURCHASED {date: datetime() - duration({days: 5}), rating: 4}]->(p)
        """
    )
    tx.run(
        """
        MATCH (u:RecUser {name: 'Alice'}), (p:RecProduct {name: 'Python Book'})
        CREATE (u)-[:PURCHASED {date: datetime() - duration({days: 20}), rating: 5}]->(p)
        """
    )

    # Bob buys similar to Alice (tech + books)
    tx.run(
        """
        MATCH (u:RecUser {name: 'Bob'}), (p:RecProduct {name: 'Laptop'})
        CREATE (u)-[:PURCHASED {date: datetime() - duration({days: 15}), rating: 4}]->(p)
        """
    )
    tx.run(
        """
        MATCH (u:RecUser {name: 'Bob'}), (p:RecProduct {name: 'Headphones'})
        CREATE (u)-[:PURCHASED {date: datetime() - duration({days: 3}), rating: 5}]->(p)
        """
    )
    tx.run(
        """
        MATCH (u:RecUser {name: 'Bob'}), (p:RecProduct {name: 'Data Science Book'})
        CREATE (u)-[:PURCHASED {date: datetime() - duration({days: 8}), rating: 4}]->(p)
        """
    )

    # Charlie buys books
    tx.run(
        """
        MATCH (u:RecUser {name: 'Charlie'}), (p:RecProduct {name: 'Python Book'})
        CREATE (u)-[:PURCHASED {date: datetime() - duration({days: 12}), rating: 5}]->(p)
        """
    )
    tx.run(
        """
        MATCH (u:RecUser {name: 'Charlie'}), (p:RecProduct {name: 'Data Science Book'})
        CREATE (u)-[:PURCHASED {date: datetime() - duration({days: 7}), rating: 5}]->(p)
        """
    )
    tx.run(
        """
        MATCH (u:RecUser {name: 'Charlie'}), (p:RecProduct {name: 'Fiction Novel'})
        CREATE (u)-[:PURCHASED {date: datetime() - duration({days: 2}), rating: 3}]->(p)
        """
    )

    # Diana buys clothes
    tx.run(
        """
        MATCH (u:RecUser {name: 'Diana'}), (p:RecProduct {name: 'T-Shirt'})
        CREATE (u)-[:PURCHASED {date: datetime() - duration({days: 4}), rating: 4}]->(p)
        """
    )
    tx.run(
        """
        MATCH (u:RecUser {name: 'Diana'}), (p:RecProduct {name: 'Jeans'})
        CREATE (u)-[:PURCHASED {date: datetime() - duration({days: 6}), rating: 5}]->(p)
        """
    )

    # Eve buys mix
    tx.run(
        """
        MATCH (u:RecUser {name: 'Eve'}), (p:RecProduct {name: 'Smartphone'})
        CREATE (u)-[:PURCHASED {date: datetime() - duration({days: 1}), rating: 5}]->(p)
        """
    )
    tx.run(
        """
        MATCH (u:RecUser {name: 'Eve'}), (p:RecProduct {name: 'T-Shirt'})
        CREATE (u)-[:PURCHASED {date: datetime() - duration({days: 9}), rating: 4}]->(p)
        """
    )

    # Frank - recent heavy buyer
    tx.run(
        """
        MATCH (u:RecUser {name: 'Frank'}), (p:RecProduct {name: 'Laptop'})
        CREATE (u)-[:PURCHASED {date: datetime() - duration({days: 2}), rating: 5}]->(p)
        """
    )
    tx.run(
        """
        MATCH (u:RecUser {name: 'Frank'}), (p:RecProduct {name: 'Headphones'})
        CREATE (u)-[:PURCHASED {date: datetime() - duration({days: 1}), rating: 4}]->(p)
        """
    )

    console.print("[green]Created recommendation graph[/green]")


def task1_collaborative_filter(tx, user_name: str, limit: int = 5) -> list[dict]:
    """
    Task 1: Find products bought by users with similar tastes.

    Solution: Classic collaborative filtering - find similar users based on
    common purchases, then recommend products they bought that you haven't.
    """
    query = """
    // Find user and their purchased products
    MATCH (user:RecUser {name: $user_name})-[:PURCHASED]->(purchased:RecProduct)
    WITH user, COLLECT(purchased) AS userProducts

    // Find similar users who bought the same products
    MATCH (user)-[:PURCHASED]->(common:RecProduct)<-[r:PURCHASED]-(similar:RecUser)
    WHERE user <> similar

    // Find products similar users bought that user hasn't
    MATCH (similar)-[r2:PURCHASED]->(rec:RecProduct)
    WHERE NOT rec IN userProducts

    // Aggregate recommendations
    RETURN rec.name AS product,
           COUNT(DISTINCT similar) AS buyerCount,
           round(AVG(r2.rating) * 10) / 10 AS avgRating
    ORDER BY buyerCount DESC, avgRating DESC
    LIMIT $limit
    """

    result = tx.run(query, user_name=user_name, limit=limit)
    return [
        {"product": r["product"], "buyerCount": r["buyerCount"], "avgRating": r["avgRating"]}
        for r in result
    ]


def task2_category_recommendations(tx, user_name: str, limit: int = 5) -> list[dict]:
    """
    Task 2: Recommend products from categories the user likes.

    Solution: Find user's favorite categories, recommend highly-rated products
    from those categories that they haven't bought.
    """
    query = """
    // Find user's favorite categories
    MATCH (user:RecUser {name: $user_name})-[:PURCHASED]->(p:RecProduct)-[:IN_CATEGORY]->(c:RecCategory)
    WITH user, c, COUNT(p) AS categoryPurchases
    ORDER BY categoryPurchases DESC
    LIMIT 2  // Top 2 categories

    // Find highly-rated products in those categories
    MATCH (rec:RecProduct)-[:IN_CATEGORY]->(c)
    WHERE NOT (user)-[:PURCHASED]->(rec)

    // Get average rating from all purchases
    OPTIONAL MATCH ()-[r:PURCHASED]->(rec)
    WITH rec, c, AVG(r.rating) AS avgRating
    WHERE avgRating IS NOT NULL

    RETURN rec.name AS product,
           c.name AS category,
           round(avgRating * 10) / 10 AS avgRating
    ORDER BY avgRating DESC
    LIMIT $limit
    """

    result = tx.run(query, user_name=user_name, limit=limit)
    return [
        {"product": r["product"], "category": r["category"], "avgRating": r["avgRating"]}
        for r in result
    ]


def task3_similar_users(tx, user_name: str, limit: int = 3) -> list[dict]:
    """
    Task 3: Find users with similar purchase patterns.

    Solution: Calculate Jaccard similarity based on common products.
    """
    query = """
    // Get user's products
    MATCH (user:RecUser {name: $user_name})-[:PURCHASED]->(p:RecProduct)
    WITH user, COLLECT(p) AS userProducts, COUNT(p) AS userCount

    // Find other users and their products
    MATCH (other:RecUser)-[:PURCHASED]->(p:RecProduct)
    WHERE other <> user
    WITH user, userProducts, userCount, other, COLLECT(p) AS otherProducts, COUNT(p) AS otherCount

    // Calculate common products
    WITH user, other, userCount, otherCount,
         [p IN userProducts WHERE p IN otherProducts] AS common
    WITH other.name AS user,
         SIZE(common) AS commonProducts,
         userCount + otherCount - SIZE(common) AS unionSize,
         SIZE(common) AS commonCount

    // Jaccard similarity = intersection / union
    RETURN user,
           commonProducts,
           round(toFloat(commonCount) / unionSize * 100) / 100 AS similarity
    ORDER BY similarity DESC
    LIMIT $limit
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

    Solution: Count purchases within time window, include rating.
    """
    query = """
    MATCH (u:RecUser)-[r:PURCHASED]->(p:RecProduct)
    WHERE r.date > datetime() - duration({days: $days})
    RETURN p.name AS product,
           COUNT(r) AS purchases,
           round(AVG(r.rating) * 10) / 10 AS avgRating
    ORDER BY purchases DESC, avgRating DESC
    LIMIT $limit
    """

    result = tx.run(query, days=days, limit=limit)
    return [
        {"product": r["product"], "purchases": r["purchases"], "avgRating": r["avgRating"]}
        for r in result
    ]


def main():
    console.print("[bold]Solution 3: Recommendation Engine[/bold]\n")

    driver = get_driver()

    try:
        driver.verify_connectivity()

        with driver.session() as session:
            # Setup data
            session.execute_write(setup_data)

            # Task 1: Collaborative filtering for Alice
            console.print("[cyan]Task 1: Collaborative Filtering for Alice[/cyan]")
            recs = session.execute_read(task1_collaborative_filter, "Alice")
            for r in recs:
                console.print(
                    f"  {r['product']}: {r['buyerCount']} similar users bought, {r['avgRating']:.1f} rating"
                )
            # Expected: Headphones, Data Science Book (bought by Bob who also has Laptop)

            # Task 2: Category recommendations
            console.print("\n[cyan]Task 2: Category-Based Recommendations for Alice[/cyan]")
            recs = session.execute_read(task2_category_recommendations, "Alice")
            for r in recs:
                console.print(f"  {r['product']} ({r['category']}): {r['avgRating']:.1f} rating")
            # Expected: Headphones (Electronics), Data Science Book (Books)

            # Task 3: Similar users to Alice
            console.print("\n[cyan]Task 3: Users Similar to Alice[/cyan]")
            similar = session.execute_read(task3_similar_users, "Alice")
            for s in similar:
                console.print(
                    f"  {s['user']}: {s['commonProducts']} common products, {s['similarity']:.2f} similarity"
                )
            # Expected: Bob (shares Laptop), Charlie (shares Python Book)

            # Task 4: Trending products
            console.print("\n[cyan]Task 4: Trending Products (Last 30 Days)[/cyan]")
            trending = session.execute_read(task4_trending_products, 30)
            for t in trending:
                console.print(
                    f"  {t['product']}: {t['purchases']} purchases, {t['avgRating']:.1f} rating"
                )
            # Expected: Laptop, Headphones (multiple recent purchases)

            # Cleanup
            session.execute_write(lambda tx: tx.run("MATCH (n:RecUser) DETACH DELETE n"))
            session.execute_write(lambda tx: tx.run("MATCH (n:RecProduct) DETACH DELETE n"))
            session.execute_write(lambda tx: tx.run("MATCH (n:RecCategory) DETACH DELETE n"))

        console.print("\n[bold green]Solution completed![/bold green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise

    finally:
        driver.close()


if __name__ == "__main__":
    main()
