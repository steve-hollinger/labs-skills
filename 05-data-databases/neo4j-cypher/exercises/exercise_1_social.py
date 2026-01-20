"""
Exercise 1: Social Network Queries

Build and query a social network graph.

Tasks:
1. Create a social network with at least 6 people and KNOWS relationships
2. Write queries to find:
   - All direct friends of a specific person
   - Mutual friends between two people
   - People with the most connections
   - Friends of friends who are not direct friends

Instructions:
- Complete the TODO sections below
- Run with: python -m exercises.exercise_1_social
- Check your answers against exercises/solutions/solution_1.py
"""

import os

from neo4j import GraphDatabase
from rich.console import Console

console = Console()


def get_driver():
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    return GraphDatabase.driver(uri, auth=(user, password))


def setup_data(tx):
    """Create the social network data."""
    # Clean up
    tx.run("MATCH (n:Friend) DETACH DELETE n")

    # TODO: Create at least 6 Friend nodes with name and age properties
    # Example: CREATE (a:Friend {name: 'Alice', age: 30})

    # TODO: Create KNOWS relationships between friends
    # Make sure to create a network where:
    # - Some people have mutual friends
    # - There are friends-of-friends connections
    # Example: CREATE (a)-[:KNOWS]->(b)

    pass  # Remove this and add your code


def task1_direct_friends(tx, person_name: str) -> list[str]:
    """
    Task 1: Find all direct friends of a person.

    Args:
        person_name: Name of the person to find friends for

    Returns:
        List of friend names
    """
    # TODO: Write a Cypher query to find all people that person_name KNOWS
    # Remember: relationships have direction, but friendships are often bidirectional
    # Hint: Use (a)-[:KNOWS]-(b) for undirected matching

    query = """
    // TODO: Your query here
    RETURN '' AS name
    """

    result = tx.run(query, name=person_name)
    return [record["name"] for record in result]


def task2_mutual_friends(tx, person1: str, person2: str) -> list[str]:
    """
    Task 2: Find mutual friends between two people.

    Args:
        person1: First person's name
        person2: Second person's name

    Returns:
        List of mutual friend names
    """
    # TODO: Write a query to find people who know BOTH person1 AND person2
    # Hint: Match two patterns from the mutual friend to each person

    query = """
    // TODO: Your query here
    RETURN '' AS name
    """

    result = tx.run(query, person1=person1, person2=person2)
    return [record["name"] for record in result]


def task3_most_connected(tx, limit: int = 3) -> list[dict]:
    """
    Task 3: Find the most connected people.

    Args:
        limit: Number of top connected people to return

    Returns:
        List of dicts with 'name' and 'connections' count
    """
    # TODO: Write a query to count KNOWS relationships per person
    # Return the top N most connected people
    # Hint: Use COUNT() and ORDER BY

    query = """
    // TODO: Your query here
    RETURN '' AS name, 0 AS connections
    """

    result = tx.run(query, limit=limit)
    return [{"name": r["name"], "connections": r["connections"]} for r in result]


def task4_friend_recommendations(tx, person_name: str) -> list[str]:
    """
    Task 4: Find friend recommendations (friends of friends who aren't direct friends).

    Args:
        person_name: Name of the person to get recommendations for

    Returns:
        List of recommended friend names
    """
    # TODO: Write a query to find friends-of-friends who are NOT direct friends
    # Hint: Use NOT (person)-[:KNOWS]-(fof) to exclude direct friends
    # Also exclude the person themselves

    query = """
    // TODO: Your query here
    RETURN '' AS name
    """

    result = tx.run(query, name=person_name)
    return [record["name"] for record in result]


def main():
    console.print("[bold]Exercise 1: Social Network Queries[/bold]\n")

    driver = get_driver()

    try:
        driver.verify_connectivity()

        with driver.session() as session:
            # Setup data
            session.execute_write(setup_data)

            # Run tasks (update person names based on your data)
            console.print("[cyan]Task 1: Direct Friends[/cyan]")
            friends = session.execute_read(task1_direct_friends, "Alice")
            console.print(f"  Alice's friends: {friends}")

            console.print("\n[cyan]Task 2: Mutual Friends[/cyan]")
            mutual = session.execute_read(task2_mutual_friends, "Alice", "Charlie")
            console.print(f"  Mutual friends of Alice and Charlie: {mutual}")

            console.print("\n[cyan]Task 3: Most Connected[/cyan]")
            connected = session.execute_read(task3_most_connected, 3)
            for person in connected:
                console.print(f"  {person['name']}: {person['connections']} connections")

            console.print("\n[cyan]Task 4: Friend Recommendations[/cyan]")
            recommendations = session.execute_read(task4_friend_recommendations, "Alice")
            console.print(f"  Recommendations for Alice: {recommendations}")

            # Cleanup
            session.execute_write(lambda tx: tx.run("MATCH (n:Friend) DETACH DELETE n"))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise

    finally:
        driver.close()


if __name__ == "__main__":
    main()
