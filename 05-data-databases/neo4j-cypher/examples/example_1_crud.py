"""
Example 1: Basic CRUD Operations

This example demonstrates fundamental Cypher operations for:
- Creating nodes with labels and properties
- Reading/querying nodes
- Updating properties
- Deleting nodes and relationships

Prerequisites:
    - Neo4j running at bolt://localhost:7687
    - Run: make infra-up from repository root
"""

import os

from neo4j import GraphDatabase
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def get_driver():
    """Create a Neo4j driver from environment variables."""
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    return GraphDatabase.driver(uri, auth=(user, password))


def cleanup_example_data(tx):
    """Remove all example data."""
    tx.run("MATCH (n:ExamplePerson) DETACH DELETE n")
    tx.run("MATCH (n:ExampleCompany) DETACH DELETE n")


def demo_create(tx):
    """Demonstrate CREATE operations."""
    console.print("\n[bold cyan]1. CREATE - Creating Nodes[/bold cyan]")

    # Create a single node
    console.print("\n[dim]Creating a single Person node:[/dim]")
    console.print(
        '[green]CREATE (p:ExamplePerson {name: "Alice", age: 30, email: "alice@example.com"})[/green]'
    )

    result = tx.run(
        """
        CREATE (p:ExamplePerson {name: 'Alice', age: 30, email: 'alice@example.com'})
        RETURN p
        """
    )
    alice = result.single()["p"]
    console.print(f"  Created: {dict(alice)}")

    # Create multiple nodes in one query
    console.print("\n[dim]Creating multiple nodes:[/dim]")
    console.print(
        '[green]CREATE (b:ExamplePerson {name: "Bob"}), (c:ExamplePerson {name: "Charlie"})[/green]'
    )

    result = tx.run(
        """
        CREATE (b:ExamplePerson {name: 'Bob', age: 25})
        CREATE (c:ExamplePerson {name: 'Charlie', age: 35})
        RETURN b, c
        """
    )
    record = result.single()
    console.print(f"  Created: {dict(record['b'])}, {dict(record['c'])}")

    # Create node with relationship
    console.print("\n[dim]Creating a node with relationship:[/dim]")
    console.print(
        '[green]MATCH (a:ExamplePerson {name: "Alice"}) CREATE (a)-[:KNOWS {since: 2020}]->(d:ExamplePerson {name: "Diana"})[/green]'
    )

    result = tx.run(
        """
        MATCH (a:ExamplePerson {name: 'Alice'})
        CREATE (a)-[:KNOWS {since: 2020}]->(d:ExamplePerson {name: 'Diana', age: 28})
        RETURN d
        """
    )
    diana = result.single()["d"]
    console.print(f"  Created: {dict(diana)} with KNOWS relationship from Alice")


def demo_read(tx):
    """Demonstrate MATCH (read) operations."""
    console.print("\n[bold cyan]2. READ - Querying with MATCH[/bold cyan]")

    # Simple match
    console.print("\n[dim]Find all ExamplePerson nodes:[/dim]")
    console.print("[green]MATCH (p:ExamplePerson) RETURN p[/green]")

    result = tx.run("MATCH (p:ExamplePerson) RETURN p ORDER BY p.name")

    table = Table(title="All Persons")
    table.add_column("Name")
    table.add_column("Age")
    table.add_column("Email")

    for record in result:
        p = record["p"]
        table.add_row(p.get("name", ""), str(p.get("age", "")), p.get("email", "-"))
    console.print(table)

    # Match with WHERE clause
    console.print("\n[dim]Find persons over 30:[/dim]")
    console.print("[green]MATCH (p:ExamplePerson) WHERE p.age > 30 RETURN p[/green]")

    result = tx.run("MATCH (p:ExamplePerson) WHERE p.age > 30 RETURN p.name, p.age")
    for record in result:
        console.print(f"  {record['p.name']}: {record['p.age']} years old")

    # Match relationships
    console.print("\n[dim]Find who Alice knows:[/dim]")
    console.print(
        '[green]MATCH (a:ExamplePerson {name: "Alice"})-[r:KNOWS]->(friend) RETURN friend, r.since[/green]'
    )

    result = tx.run(
        """
        MATCH (a:ExamplePerson {name: 'Alice'})-[r:KNOWS]->(friend)
        RETURN friend.name AS name, r.since AS since
        """
    )
    for record in result:
        console.print(f"  Alice knows {record['name']} since {record['since']}")


def demo_update(tx):
    """Demonstrate SET (update) operations."""
    console.print("\n[bold cyan]3. UPDATE - Modifying with SET[/bold cyan]")

    # Update single property
    console.print("\n[dim]Update Alice's age:[/dim]")
    console.print('[green]MATCH (p:ExamplePerson {name: "Alice"}) SET p.age = 31[/green]')

    result = tx.run(
        """
        MATCH (p:ExamplePerson {name: 'Alice'})
        SET p.age = 31
        RETURN p.name, p.age
        """
    )
    record = result.single()
    console.print(f"  Updated: {record['p.name']} is now {record['p.age']}")

    # Add new property
    console.print("\n[dim]Add a new property to Bob:[/dim]")
    console.print(
        '[green]MATCH (p:ExamplePerson {name: "Bob"}) SET p.department = "Engineering"[/green]'
    )

    result = tx.run(
        """
        MATCH (p:ExamplePerson {name: 'Bob'})
        SET p.department = 'Engineering'
        RETURN p
        """
    )
    bob = result.single()["p"]
    console.print(f"  Updated: {dict(bob)}")

    # Update multiple properties with map
    console.print("\n[dim]Update Charlie with multiple properties:[/dim]")
    console.print(
        '[green]MATCH (p:ExamplePerson {name: "Charlie"}) SET p += {city: "NYC", role: "Manager"}[/green]'
    )

    result = tx.run(
        """
        MATCH (p:ExamplePerson {name: 'Charlie'})
        SET p += {city: 'NYC', role: 'Manager'}
        RETURN p
        """
    )
    charlie = result.single()["p"]
    console.print(f"  Updated: {dict(charlie)}")


def demo_merge(tx):
    """Demonstrate MERGE operations."""
    console.print("\n[bold cyan]4. MERGE - Create If Not Exists[/bold cyan]")

    # MERGE node
    console.print("\n[dim]MERGE finds existing or creates new:[/dim]")
    console.print('[green]MERGE (p:ExamplePerson {name: "Alice"}) RETURN p[/green]')

    result = tx.run(
        """
        MERGE (p:ExamplePerson {name: 'Alice'})
        RETURN p, p.age AS age
        """
    )
    record = result.single()
    console.print(f"  Found existing Alice with age {record['age']}")

    # MERGE with ON CREATE/ON MATCH
    console.print("\n[dim]MERGE with conditional updates:[/dim]")
    console.print("[green]MERGE (p:ExamplePerson {name: $name})[/green]")
    console.print("[green]ON CREATE SET p.created = datetime()[/green]")
    console.print("[green]ON MATCH SET p.lastSeen = datetime()[/green]")

    # Try with existing (Alice)
    result = tx.run(
        """
        MERGE (p:ExamplePerson {name: 'Alice'})
        ON CREATE SET p.created = datetime()
        ON MATCH SET p.lastSeen = datetime()
        RETURN p,
               CASE WHEN p.lastSeen IS NOT NULL THEN 'matched' ELSE 'created' END AS action
        """
    )
    record = result.single()
    console.print(f"  Alice: {record['action']} (lastSeen set)")

    # Try with new (Eve)
    result = tx.run(
        """
        MERGE (p:ExamplePerson {name: 'Eve'})
        ON CREATE SET p.created = datetime(), p.age = 26
        ON MATCH SET p.lastSeen = datetime()
        RETURN p,
               CASE WHEN p.created IS NOT NULL AND p.lastSeen IS NULL THEN 'created' ELSE 'matched' END AS action
        """
    )
    record = result.single()
    console.print(f"  Eve: {record['action']} (new node)")


def demo_delete(tx):
    """Demonstrate DELETE operations."""
    console.print("\n[bold cyan]5. DELETE - Removing Data[/bold cyan]")

    # Delete property with REMOVE
    console.print("\n[dim]Remove a property:[/dim]")
    console.print('[green]MATCH (p:ExamplePerson {name: "Bob"}) REMOVE p.department[/green]')

    tx.run(
        """
        MATCH (p:ExamplePerson {name: 'Bob'})
        REMOVE p.department
        """
    )
    console.print("  Removed department from Bob")

    # Delete relationship
    console.print("\n[dim]Delete a relationship:[/dim]")
    console.print(
        '[green]MATCH (a:ExamplePerson {name: "Alice"})-[r:KNOWS]->(d:ExamplePerson {name: "Diana"}) DELETE r[/green]'
    )

    result = tx.run(
        """
        MATCH (a:ExamplePerson {name: 'Alice'})-[r:KNOWS]->(d:ExamplePerson {name: 'Diana'})
        DELETE r
        RETURN count(r) AS deleted
        """
    )
    console.print(f"  Deleted {result.single()['deleted']} relationship(s)")

    # Delete node (without relationships)
    console.print("\n[dim]Delete a node (Diana, now has no relationships):[/dim]")
    console.print('[green]MATCH (p:ExamplePerson {name: "Diana"}) DELETE p[/green]')

    result = tx.run(
        """
        MATCH (p:ExamplePerson {name: 'Diana'})
        DELETE p
        RETURN count(p) AS deleted
        """
    )
    console.print(f"  Deleted {result.single()['deleted']} node(s)")

    # DETACH DELETE - delete node with all its relationships
    console.print("\n[dim]DETACH DELETE - delete node and all relationships:[/dim]")
    console.print('[green]MATCH (p:ExamplePerson {name: "Eve"}) DETACH DELETE p[/green]')

    result = tx.run(
        """
        MATCH (p:ExamplePerson {name: 'Eve'})
        DETACH DELETE p
        RETURN count(p) AS deleted
        """
    )
    console.print(f"  Deleted {result.single()['deleted']} node(s) with relationships")


def main():
    """Run all CRUD examples."""
    console.print(Panel.fit("[bold]Neo4j Cypher - Example 1: Basic CRUD Operations[/bold]"))

    driver = get_driver()

    try:
        # Verify connection
        driver.verify_connectivity()
        console.print("[green]Connected to Neo4j![/green]")

        with driver.session() as session:
            # Clean up any existing example data
            session.execute_write(cleanup_example_data)

            # Run demos
            session.execute_write(demo_create)
            session.execute_read(demo_read)
            session.execute_write(demo_update)
            session.execute_write(demo_merge)
            session.execute_write(demo_delete)

            # Final cleanup
            session.execute_write(cleanup_example_data)
            console.print("\n[dim]Cleaned up example data[/dim]")

        console.print("\n[bold green]Example completed successfully![/bold green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("[yellow]Make sure Neo4j is running: make infra-up[/yellow]")
        raise

    finally:
        driver.close()


if __name__ == "__main__":
    main()
