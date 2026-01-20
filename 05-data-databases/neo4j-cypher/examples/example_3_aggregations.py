"""
Example 3: Aggregations and Path Queries

This example demonstrates:
- Aggregation functions (COUNT, SUM, AVG, COLLECT)
- Grouping and sorting
- Variable-length paths
- Shortest path algorithms
- Path functions

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


def setup_social_network(tx):
    """Create a sample social network."""
    # Clean up existing data
    tx.run("MATCH (n:SocialPerson) DETACH DELETE n")
    tx.run("MATCH (n:SocialCompany) DETACH DELETE n")

    # Create people with various properties
    tx.run(
        """
        CREATE (alice:SocialPerson {name: 'Alice', age: 30, city: 'NYC', salary: 85000})
        CREATE (bob:SocialPerson {name: 'Bob', age: 25, city: 'NYC', salary: 72000})
        CREATE (charlie:SocialPerson {name: 'Charlie', age: 35, city: 'LA', salary: 95000})
        CREATE (diana:SocialPerson {name: 'Diana', age: 28, city: 'NYC', salary: 78000})
        CREATE (eve:SocialPerson {name: 'Eve', age: 32, city: 'LA', salary: 88000})
        CREATE (frank:SocialPerson {name: 'Frank', age: 40, city: 'Chicago', salary: 105000})
        CREATE (grace:SocialPerson {name: 'Grace', age: 27, city: 'Chicago', salary: 68000})
        CREATE (henry:SocialPerson {name: 'Henry', age: 45, city: 'NYC', salary: 120000})
        """
    )

    # Create companies
    tx.run(
        """
        CREATE (tech:SocialCompany {name: 'TechCorp', industry: 'Technology'})
        CREATE (finance:SocialCompany {name: 'FinanceInc', industry: 'Finance'})
        """
    )

    # Create KNOWS relationships (social network)
    tx.run(
        """
        MATCH (a:SocialPerson {name: 'Alice'}), (b:SocialPerson {name: 'Bob'})
        CREATE (a)-[:KNOWS {since: 2018, strength: 'close'}]->(b)
        """
    )
    tx.run(
        """
        MATCH (a:SocialPerson {name: 'Alice'}), (c:SocialPerson {name: 'Charlie'})
        CREATE (a)-[:KNOWS {since: 2020, strength: 'acquaintance'}]->(c)
        """
    )
    tx.run(
        """
        MATCH (b:SocialPerson {name: 'Bob'}), (d:SocialPerson {name: 'Diana'})
        CREATE (b)-[:KNOWS {since: 2019, strength: 'close'}]->(d)
        """
    )
    tx.run(
        """
        MATCH (c:SocialPerson {name: 'Charlie'}), (e:SocialPerson {name: 'Eve'})
        CREATE (c)-[:KNOWS {since: 2017, strength: 'close'}]->(e)
        """
    )
    tx.run(
        """
        MATCH (d:SocialPerson {name: 'Diana'}), (e:SocialPerson {name: 'Eve'})
        CREATE (d)-[:KNOWS {since: 2021, strength: 'acquaintance'}]->(e)
        """
    )
    tx.run(
        """
        MATCH (e:SocialPerson {name: 'Eve'}), (f:SocialPerson {name: 'Frank'})
        CREATE (e)-[:KNOWS {since: 2016, strength: 'close'}]->(f)
        """
    )
    tx.run(
        """
        MATCH (f:SocialPerson {name: 'Frank'}), (g:SocialPerson {name: 'Grace'})
        CREATE (f)-[:KNOWS {since: 2015, strength: 'close'}]->(g)
        """
    )
    tx.run(
        """
        MATCH (g:SocialPerson {name: 'Grace'}), (h:SocialPerson {name: 'Henry'})
        CREATE (g)-[:KNOWS {since: 2020, strength: 'acquaintance'}]->(h)
        """
    )

    # Create WORKS_AT relationships
    tx.run(
        """
        MATCH (p:SocialPerson), (c:SocialCompany {name: 'TechCorp'})
        WHERE p.name IN ['Alice', 'Bob', 'Charlie', 'Diana']
        CREATE (p)-[:WORKS_AT {since: 2020}]->(c)
        """
    )
    tx.run(
        """
        MATCH (p:SocialPerson), (c:SocialCompany {name: 'FinanceInc'})
        WHERE p.name IN ['Eve', 'Frank', 'Grace', 'Henry']
        CREATE (p)-[:WORKS_AT {since: 2019}]->(c)
        """
    )

    console.print("[green]Created social network with 8 people and 2 companies[/green]")


def demo_basic_aggregations(tx):
    """Demonstrate basic aggregation functions."""
    console.print("\n[bold cyan]1. Basic Aggregations[/bold cyan]")

    # COUNT
    console.print("\n[dim]Count people by city:[/dim]")
    console.print("[green]MATCH (p:SocialPerson) RETURN p.city, COUNT(p) AS count[/green]")

    result = tx.run(
        """
        MATCH (p:SocialPerson)
        RETURN p.city AS city, COUNT(p) AS count
        ORDER BY count DESC
        """
    )

    table = Table(title="People by City")
    table.add_column("City")
    table.add_column("Count", justify="right")

    for record in result:
        table.add_row(record["city"], str(record["count"]))
    console.print(table)

    # Multiple aggregations
    console.print("\n[dim]Salary statistics by city:[/dim]")
    console.print(
        "[green]MATCH (p:SocialPerson) RETURN p.city, AVG(p.salary), MIN(p.salary), MAX(p.salary)[/green]"
    )

    result = tx.run(
        """
        MATCH (p:SocialPerson)
        RETURN p.city AS city,
               COUNT(p) AS people,
               round(AVG(p.salary)) AS avgSalary,
               MIN(p.salary) AS minSalary,
               MAX(p.salary) AS maxSalary
        ORDER BY avgSalary DESC
        """
    )

    table = Table(title="Salary Statistics by City")
    table.add_column("City")
    table.add_column("People", justify="right")
    table.add_column("Avg Salary", justify="right")
    table.add_column("Min", justify="right")
    table.add_column("Max", justify="right")

    for record in result:
        table.add_row(
            record["city"],
            str(record["people"]),
            f"${record['avgSalary']:,.0f}",
            f"${record['minSalary']:,}",
            f"${record['maxSalary']:,}",
        )
    console.print(table)


def demo_collect_aggregation(tx):
    """Demonstrate COLLECT for building lists."""
    console.print("\n[bold cyan]2. COLLECT - Building Lists[/bold cyan]")

    # Collect names by city
    console.print("\n[dim]Collect people names by city:[/dim]")
    console.print("[green]MATCH (p:SocialPerson) RETURN p.city, COLLECT(p.name)[/green]")

    result = tx.run(
        """
        MATCH (p:SocialPerson)
        RETURN p.city AS city, COLLECT(p.name) AS people
        ORDER BY city
        """
    )

    for record in result:
        console.print(f"  [bold]{record['city']}[/bold]: {', '.join(record['people'])}")

    # Collect with transformation
    console.print("\n[dim]Collect with property selection:[/dim]")
    console.print(
        "[green]MATCH (p)-[:WORKS_AT]->(c:SocialCompany) RETURN c.name, COLLECT({name: p.name, salary: p.salary})[/green]"
    )

    result = tx.run(
        """
        MATCH (p:SocialPerson)-[:WORKS_AT]->(c:SocialCompany)
        RETURN c.name AS company,
               COLLECT({name: p.name, salary: p.salary}) AS employees,
               SUM(p.salary) AS totalSalary
        ORDER BY company
        """
    )

    for record in result:
        console.print(f"\n  [bold]{record['company']}[/bold] (Total: ${record['totalSalary']:,})")
        for emp in record["employees"]:
            console.print(f"    - {emp['name']}: ${emp['salary']:,}")


def demo_relationship_aggregations(tx):
    """Demonstrate aggregations on relationships."""
    console.print("\n[bold cyan]3. Relationship Aggregations[/bold cyan]")

    # Count connections per person
    console.print("\n[dim]Count outgoing KNOWS relationships:[/dim]")
    console.print(
        "[green]MATCH (p:SocialPerson)-[r:KNOWS]->() RETURN p.name, COUNT(r) AS connections[/green]"
    )

    result = tx.run(
        """
        MATCH (p:SocialPerson)
        OPTIONAL MATCH (p)-[r:KNOWS]->()
        RETURN p.name AS person, COUNT(r) AS outgoingConnections
        ORDER BY outgoingConnections DESC
        """
    )

    table = Table(title="Connections per Person")
    table.add_column("Person")
    table.add_column("Outgoing Connections", justify="right")

    for record in result:
        table.add_row(record["person"], str(record["outgoingConnections"]))
    console.print(table)

    # Group by relationship property
    console.print("\n[dim]Count relationships by strength:[/dim]")

    result = tx.run(
        """
        MATCH ()-[r:KNOWS]->()
        RETURN r.strength AS strength, COUNT(r) AS count
        ORDER BY count DESC
        """
    )

    for record in result:
        console.print(f"  {record['strength']}: {record['count']} relationships")


def demo_variable_length_paths(tx):
    """Demonstrate variable-length path queries."""
    console.print("\n[bold cyan]4. Variable-Length Paths[/bold cyan]")

    # Find friends at exact depth
    console.print("\n[dim]Find Alice's friends of friends (exactly 2 hops):[/dim]")
    console.print('[green]MATCH (alice {name: "Alice"})-[:KNOWS*2]->(fof) RETURN DISTINCT fof.name[/green]')

    result = tx.run(
        """
        MATCH (alice:SocialPerson {name: 'Alice'})-[:KNOWS*2]->(fof:SocialPerson)
        WHERE alice <> fof
        RETURN DISTINCT fof.name AS friendOfFriend
        ORDER BY friendOfFriend
        """
    )

    console.print("  Alice's Friends of Friends:")
    for record in result:
        console.print(f"    - {record['friendOfFriend']}")

    # Variable range
    console.print("\n[dim]Find connections within 1-3 hops:[/dim]")
    console.print('[green]MATCH path = (alice {name: "Alice"})-[:KNOWS*1..3]->(connected)[/green]')

    result = tx.run(
        """
        MATCH path = (alice:SocialPerson {name: 'Alice'})-[:KNOWS*1..3]->(connected:SocialPerson)
        WHERE alice <> connected
        RETURN DISTINCT connected.name AS person, length(path) AS distance
        ORDER BY distance, person
        """
    )

    table = Table(title="Alice's Network (1-3 hops)")
    table.add_column("Person")
    table.add_column("Distance", justify="right")

    for record in result:
        table.add_row(record["person"], str(record["distance"]))
    console.print(table)


def demo_shortest_path(tx):
    """Demonstrate shortest path algorithms."""
    console.print("\n[bold cyan]5. Shortest Path[/bold cyan]")

    # Find shortest path between two people
    console.print("\n[dim]Find shortest path from Alice to Henry:[/dim]")
    console.print(
        '[green]MATCH path = shortestPath((a {name: "Alice"})-[:KNOWS*]-(b {name: "Henry"}))[/green]'
    )

    result = tx.run(
        """
        MATCH path = shortestPath(
            (a:SocialPerson {name: 'Alice'})-[:KNOWS*]-(b:SocialPerson {name: 'Henry'})
        )
        RETURN path,
               [n IN nodes(path) | n.name] AS people,
               length(path) AS hops
        """
    )

    record = result.single()
    if record:
        console.print(f"  Path: {' -> '.join(record['people'])}")
        console.print(f"  Hops: {record['hops']}")
    else:
        console.print("  [yellow]No path found[/yellow]")

    # All shortest paths
    console.print("\n[dim]Find all shortest paths from Alice to Frank:[/dim]")
    console.print(
        '[green]MATCH path = allShortestPaths((a {name: "Alice"})-[:KNOWS*]-(b {name: "Frank"}))[/green]'
    )

    result = tx.run(
        """
        MATCH path = allShortestPaths(
            (a:SocialPerson {name: 'Alice'})-[:KNOWS*]-(b:SocialPerson {name: 'Frank'})
        )
        RETURN [n IN nodes(path) | n.name] AS people,
               length(path) AS hops
        LIMIT 5
        """
    )

    for i, record in enumerate(result, 1):
        console.print(f"  Path {i}: {' -> '.join(record['people'])} ({record['hops']} hops)")


def demo_path_functions(tx):
    """Demonstrate path analysis functions."""
    console.print("\n[bold cyan]6. Path Functions[/bold cyan]")

    console.print("\n[dim]Analyze path components:[/dim]")
    console.print("[green]nodes(path), relationships(path), length(path)[/green]")

    result = tx.run(
        """
        MATCH path = (a:SocialPerson {name: 'Alice'})-[:KNOWS*3]->(d:SocialPerson)
        RETURN
            [n IN nodes(path) | n.name] AS nodeNames,
            [r IN relationships(path) | r.strength] AS relStrengths,
            length(path) AS pathLength
        LIMIT 3
        """
    )

    for i, record in enumerate(result, 1):
        console.print(f"\n  Path {i}:")
        console.print(f"    Nodes: {' -> '.join(record['nodeNames'])}")
        console.print(f"    Relationship strengths: {' -> '.join(record['relStrengths'])}")
        console.print(f"    Length: {record['pathLength']}")


def demo_with_clause(tx):
    """Demonstrate WITH for query chaining and filtering."""
    console.print("\n[bold cyan]7. WITH Clause - Query Chaining[/bold cyan]")

    # Filter aggregated results
    console.print("\n[dim]Find cities with more than 2 people:[/dim]")
    console.print(
        "[green]MATCH (p) WITH p.city AS city, COUNT(p) AS count WHERE count > 2 RETURN city[/green]"
    )

    result = tx.run(
        """
        MATCH (p:SocialPerson)
        WITH p.city AS city, COUNT(p) AS count
        WHERE count > 2
        RETURN city, count
        ORDER BY count DESC
        """
    )

    for record in result:
        console.print(f"  {record['city']}: {record['count']} people")

    # Chain multiple operations
    console.print("\n[dim]Find top earners and their friends:[/dim]")
    console.print(
        "[green]MATCH (p) WITH p ORDER BY p.salary DESC LIMIT 3 MATCH (p)-[:KNOWS]->(friend)[/green]"
    )

    result = tx.run(
        """
        MATCH (p:SocialPerson)
        WITH p
        ORDER BY p.salary DESC
        LIMIT 3
        OPTIONAL MATCH (p)-[:KNOWS]->(friend:SocialPerson)
        RETURN p.name AS topEarner,
               p.salary AS salary,
               COLLECT(friend.name) AS friends
        """
    )

    for record in result:
        friends = [f for f in record["friends"] if f]
        console.print(f"\n  [bold]{record['topEarner']}[/bold] (${record['salary']:,})")
        if friends:
            console.print(f"    Friends: {', '.join(friends)}")
        else:
            console.print("    Friends: [dim]None[/dim]")


def cleanup(tx):
    """Clean up all example data."""
    tx.run("MATCH (n:SocialPerson) DETACH DELETE n")
    tx.run("MATCH (n:SocialCompany) DETACH DELETE n")


def main():
    """Run all aggregation and path examples."""
    console.print(Panel.fit("[bold]Neo4j Cypher - Example 3: Aggregations and Paths[/bold]"))

    driver = get_driver()

    try:
        driver.verify_connectivity()
        console.print("[green]Connected to Neo4j![/green]")

        with driver.session() as session:
            # Setup test data
            session.execute_write(setup_social_network)

            # Run demos
            session.execute_read(demo_basic_aggregations)
            session.execute_read(demo_collect_aggregation)
            session.execute_read(demo_relationship_aggregations)
            session.execute_read(demo_variable_length_paths)
            session.execute_read(demo_shortest_path)
            session.execute_read(demo_path_functions)
            session.execute_read(demo_with_clause)

            # Cleanup
            session.execute_write(cleanup)
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
