"""
Solution 1: Social Network Queries

Complete solution for Exercise 1.
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

    # Create friends
    tx.run(
        """
        CREATE (alice:Friend {name: 'Alice', age: 30})
        CREATE (bob:Friend {name: 'Bob', age: 25})
        CREATE (charlie:Friend {name: 'Charlie', age: 35})
        CREATE (diana:Friend {name: 'Diana', age: 28})
        CREATE (eve:Friend {name: 'Eve', age: 32})
        CREATE (frank:Friend {name: 'Frank', age: 40})
        """
    )

    # Create KNOWS relationships (bidirectional friendships)
    tx.run(
        """
        MATCH (alice:Friend {name: 'Alice'}), (bob:Friend {name: 'Bob'})
        CREATE (alice)-[:KNOWS]->(bob)
        CREATE (bob)-[:KNOWS]->(alice)
        """
    )
    tx.run(
        """
        MATCH (alice:Friend {name: 'Alice'}), (charlie:Friend {name: 'Charlie'})
        CREATE (alice)-[:KNOWS]->(charlie)
        CREATE (charlie)-[:KNOWS]->(alice)
        """
    )
    tx.run(
        """
        MATCH (bob:Friend {name: 'Bob'}), (charlie:Friend {name: 'Charlie'})
        CREATE (bob)-[:KNOWS]->(charlie)
        CREATE (charlie)-[:KNOWS]->(bob)
        """
    )
    tx.run(
        """
        MATCH (bob:Friend {name: 'Bob'}), (diana:Friend {name: 'Diana'})
        CREATE (bob)-[:KNOWS]->(diana)
        CREATE (diana)-[:KNOWS]->(bob)
        """
    )
    tx.run(
        """
        MATCH (charlie:Friend {name: 'Charlie'}), (eve:Friend {name: 'Eve'})
        CREATE (charlie)-[:KNOWS]->(eve)
        CREATE (eve)-[:KNOWS]->(charlie)
        """
    )
    tx.run(
        """
        MATCH (diana:Friend {name: 'Diana'}), (eve:Friend {name: 'Eve'})
        CREATE (diana)-[:KNOWS]->(eve)
        CREATE (eve)-[:KNOWS]->(diana)
        """
    )
    tx.run(
        """
        MATCH (eve:Friend {name: 'Eve'}), (frank:Friend {name: 'Frank'})
        CREATE (eve)-[:KNOWS]->(frank)
        CREATE (frank)-[:KNOWS]->(eve)
        """
    )

    console.print("[green]Created social network[/green]")


def task1_direct_friends(tx, person_name: str) -> list[str]:
    """
    Task 1: Find all direct friends of a person.

    Solution: Use undirected KNOWS matching to find friends regardless of
    which direction the relationship was created.
    """
    query = """
    MATCH (person:Friend {name: $name})-[:KNOWS]-(friend:Friend)
    RETURN DISTINCT friend.name AS name
    ORDER BY name
    """

    result = tx.run(query, name=person_name)
    return [record["name"] for record in result]


def task2_mutual_friends(tx, person1: str, person2: str) -> list[str]:
    """
    Task 2: Find mutual friends between two people.

    Solution: Find people who have KNOWS relationships with BOTH people.
    """
    query = """
    MATCH (p1:Friend {name: $person1})-[:KNOWS]-(mutual:Friend)-[:KNOWS]-(p2:Friend {name: $person2})
    WHERE p1 <> p2 AND mutual <> p1 AND mutual <> p2
    RETURN DISTINCT mutual.name AS name
    ORDER BY name
    """

    result = tx.run(query, person1=person1, person2=person2)
    return [record["name"] for record in result]


def task3_most_connected(tx, limit: int = 3) -> list[dict]:
    """
    Task 3: Find the most connected people.

    Solution: Count KNOWS relationships per person and order by count.
    Using undirected matching counts both incoming and outgoing.
    """
    query = """
    MATCH (person:Friend)-[r:KNOWS]-(:Friend)
    RETURN person.name AS name, COUNT(r) AS connections
    ORDER BY connections DESC
    LIMIT $limit
    """

    result = tx.run(query, limit=limit)
    return [{"name": r["name"], "connections": r["connections"]} for r in result]


def task4_friend_recommendations(tx, person_name: str) -> list[str]:
    """
    Task 4: Find friend recommendations (friends of friends who aren't direct friends).

    Solution: Find friends of friends, excluding direct friends and self.
    """
    query = """
    MATCH (person:Friend {name: $name})-[:KNOWS]-(friend:Friend)-[:KNOWS]-(fof:Friend)
    WHERE NOT (person)-[:KNOWS]-(fof)
      AND person <> fof
    RETURN DISTINCT fof.name AS name
    ORDER BY name
    """

    result = tx.run(query, name=person_name)
    return [record["name"] for record in result]


def main():
    console.print("[bold]Solution 1: Social Network Queries[/bold]\n")

    driver = get_driver()

    try:
        driver.verify_connectivity()

        with driver.session() as session:
            # Setup data
            session.execute_write(setup_data)

            # Task 1
            console.print("[cyan]Task 1: Direct Friends of Alice[/cyan]")
            friends = session.execute_read(task1_direct_friends, "Alice")
            console.print(f"  Alice's friends: {friends}")
            # Expected: ['Bob', 'Charlie']

            # Task 2
            console.print("\n[cyan]Task 2: Mutual Friends of Alice and Diana[/cyan]")
            mutual = session.execute_read(task2_mutual_friends, "Alice", "Diana")
            console.print(f"  Mutual friends: {mutual}")
            # Expected: ['Bob'] (Bob knows both Alice and Diana)

            # Task 3
            console.print("\n[cyan]Task 3: Most Connected People[/cyan]")
            connected = session.execute_read(task3_most_connected, 3)
            for person in connected:
                console.print(f"  {person['name']}: {person['connections']} connections")
            # Expected: Charlie and Eve likely have most connections

            # Task 4
            console.print("\n[cyan]Task 4: Friend Recommendations for Alice[/cyan]")
            recommendations = session.execute_read(task4_friend_recommendations, "Alice")
            console.print(f"  Recommendations: {recommendations}")
            # Expected: Diana (friend of Bob), Eve (friend of Charlie)

            # Cleanup
            session.execute_write(lambda tx: tx.run("MATCH (n:Friend) DETACH DELETE n"))

        console.print("\n[bold green]Solution completed![/bold green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise

    finally:
        driver.close()


if __name__ == "__main__":
    main()
