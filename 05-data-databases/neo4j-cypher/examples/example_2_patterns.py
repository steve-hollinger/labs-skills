"""
Example 2: Pattern Matching and Relationships

This example demonstrates advanced pattern matching:
- Complex relationship patterns
- Multiple relationship types
- Bi-directional queries
- Optional matches
- Pattern comprehension

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


def setup_movie_data(tx):
    """Create a sample movie database."""
    # Clean up existing data
    tx.run("MATCH (n:Movie) DETACH DELETE n")
    tx.run("MATCH (n:Actor) DETACH DELETE n")
    tx.run("MATCH (n:Director) DETACH DELETE n")

    # Create movies
    tx.run(
        """
        CREATE (m1:Movie {title: 'The Matrix', year: 1999, genre: 'Sci-Fi'})
        CREATE (m2:Movie {title: 'The Matrix Reloaded', year: 2003, genre: 'Sci-Fi'})
        CREATE (m3:Movie {title: 'John Wick', year: 2014, genre: 'Action'})
        CREATE (m4:Movie {title: 'Speed', year: 1994, genre: 'Action'})
        CREATE (m5:Movie {title: 'Point Break', year: 1991, genre: 'Action'})
        """
    )

    # Create actors
    tx.run(
        """
        CREATE (a1:Actor {name: 'Keanu Reeves', born: 1964})
        CREATE (a2:Actor {name: 'Carrie-Anne Moss', born: 1967})
        CREATE (a3:Actor {name: 'Laurence Fishburne', born: 1961})
        CREATE (a4:Actor {name: 'Hugo Weaving', born: 1960})
        CREATE (a5:Actor {name: 'Sandra Bullock', born: 1964})
        """
    )

    # Create directors
    tx.run(
        """
        CREATE (d1:Director {name: 'Lana Wachowski', born: 1965})
        CREATE (d2:Director {name: 'Lilly Wachowski', born: 1967})
        CREATE (d3:Director {name: 'Chad Stahelski', born: 1968})
        """
    )

    # Create ACTED_IN relationships
    tx.run(
        """
        MATCH (a:Actor {name: 'Keanu Reeves'}), (m:Movie {title: 'The Matrix'})
        CREATE (a)-[:ACTED_IN {role: 'Neo'}]->(m)
        """
    )
    tx.run(
        """
        MATCH (a:Actor {name: 'Keanu Reeves'}), (m:Movie {title: 'The Matrix Reloaded'})
        CREATE (a)-[:ACTED_IN {role: 'Neo'}]->(m)
        """
    )
    tx.run(
        """
        MATCH (a:Actor {name: 'Keanu Reeves'}), (m:Movie {title: 'John Wick'})
        CREATE (a)-[:ACTED_IN {role: 'John Wick'}]->(m)
        """
    )
    tx.run(
        """
        MATCH (a:Actor {name: 'Keanu Reeves'}), (m:Movie {title: 'Speed'})
        CREATE (a)-[:ACTED_IN {role: 'Jack Traven'}]->(m)
        """
    )
    tx.run(
        """
        MATCH (a:Actor {name: 'Keanu Reeves'}), (m:Movie {title: 'Point Break'})
        CREATE (a)-[:ACTED_IN {role: 'Johnny Utah'}]->(m)
        """
    )

    tx.run(
        """
        MATCH (a:Actor {name: 'Carrie-Anne Moss'}), (m:Movie {title: 'The Matrix'})
        CREATE (a)-[:ACTED_IN {role: 'Trinity'}]->(m)
        """
    )
    tx.run(
        """
        MATCH (a:Actor {name: 'Carrie-Anne Moss'}), (m:Movie {title: 'The Matrix Reloaded'})
        CREATE (a)-[:ACTED_IN {role: 'Trinity'}]->(m)
        """
    )

    tx.run(
        """
        MATCH (a:Actor {name: 'Laurence Fishburne'}), (m:Movie {title: 'The Matrix'})
        CREATE (a)-[:ACTED_IN {role: 'Morpheus'}]->(m)
        """
    )
    tx.run(
        """
        MATCH (a:Actor {name: 'Laurence Fishburne'}), (m:Movie {title: 'The Matrix Reloaded'})
        CREATE (a)-[:ACTED_IN {role: 'Morpheus'}]->(m)
        """
    )

    tx.run(
        """
        MATCH (a:Actor {name: 'Hugo Weaving'}), (m:Movie {title: 'The Matrix'})
        CREATE (a)-[:ACTED_IN {role: 'Agent Smith'}]->(m)
        """
    )

    tx.run(
        """
        MATCH (a:Actor {name: 'Sandra Bullock'}), (m:Movie {title: 'Speed'})
        CREATE (a)-[:ACTED_IN {role: 'Annie Porter'}]->(m)
        """
    )

    # Create DIRECTED relationships
    tx.run(
        """
        MATCH (d:Director {name: 'Lana Wachowski'}), (m:Movie)
        WHERE m.title IN ['The Matrix', 'The Matrix Reloaded']
        CREATE (d)-[:DIRECTED]->(m)
        """
    )
    tx.run(
        """
        MATCH (d:Director {name: 'Lilly Wachowski'}), (m:Movie)
        WHERE m.title IN ['The Matrix', 'The Matrix Reloaded']
        CREATE (d)-[:DIRECTED]->(m)
        """
    )
    tx.run(
        """
        MATCH (d:Director {name: 'Chad Stahelski'}), (m:Movie {title: 'John Wick'})
        CREATE (d)-[:DIRECTED]->(m)
        """
    )

    console.print("[green]Created movie database with actors, directors, and relationships[/green]")


def demo_basic_patterns(tx):
    """Demonstrate basic pattern matching."""
    console.print("\n[bold cyan]1. Basic Pattern Matching[/bold cyan]")

    # Simple relationship pattern
    console.print("\n[dim]Find all actors and their movies:[/dim]")
    console.print("[green]MATCH (a:Actor)-[r:ACTED_IN]->(m:Movie) RETURN a.name, r.role, m.title[/green]")

    result = tx.run(
        """
        MATCH (a:Actor)-[r:ACTED_IN]->(m:Movie)
        RETURN a.name AS actor, r.role AS role, m.title AS movie
        ORDER BY a.name, m.year
        """
    )

    table = Table(title="Actors and Movies")
    table.add_column("Actor")
    table.add_column("Role")
    table.add_column("Movie")

    for record in result:
        table.add_row(record["actor"], record["role"], record["movie"])
    console.print(table)


def demo_multiple_relationships(tx):
    """Demonstrate patterns with multiple relationship types."""
    console.print("\n[bold cyan]2. Multiple Relationship Types[/bold cyan]")

    # Find movies with their cast and directors
    console.print("\n[dim]Find movies with actors AND directors:[/dim]")
    console.print(
        "[green]MATCH (a:Actor)-[:ACTED_IN]->(m:Movie)<-[:DIRECTED]-(d:Director)[/green]"
    )

    result = tx.run(
        """
        MATCH (a:Actor)-[:ACTED_IN]->(m:Movie)<-[:DIRECTED]-(d:Director)
        RETURN m.title AS movie, collect(DISTINCT a.name) AS actors, collect(DISTINCT d.name) AS directors
        ORDER BY m.title
        """
    )

    for record in result:
        console.print(f"\n  [bold]{record['movie']}[/bold]")
        console.print(f"    Directors: {', '.join(record['directors'])}")
        console.print(f"    Actors: {', '.join(record['actors'])}")


def demo_undirected_patterns(tx):
    """Demonstrate undirected (bi-directional) patterns."""
    console.print("\n[bold cyan]3. Undirected Patterns[/bold cyan]")

    # Find all connections to a movie (either direction)
    console.print("\n[dim]Find ALL connections to The Matrix (any direction):[/dim]")
    console.print('[green]MATCH (m:Movie {title: "The Matrix"})-[r]-(connected)[/green]')

    result = tx.run(
        """
        MATCH (m:Movie {title: 'The Matrix'})-[r]-(connected)
        RETURN type(r) AS relationship,
               labels(connected)[0] AS nodeType,
               coalesce(connected.name, connected.title) AS name
        ORDER BY relationship, name
        """
    )

    table = Table(title="Connections to The Matrix")
    table.add_column("Relationship")
    table.add_column("Type")
    table.add_column("Name")

    for record in result:
        table.add_row(record["relationship"], record["nodeType"], record["name"])
    console.print(table)


def demo_complex_patterns(tx):
    """Demonstrate complex multi-hop patterns."""
    console.print("\n[bold cyan]4. Complex Multi-Hop Patterns[/bold cyan]")

    # Find actors who worked with the same director
    console.print("\n[dim]Find actors who worked with both Wachowskis:[/dim]")
    console.print(
        "[green]MATCH (a:Actor)-[:ACTED_IN]->(m:Movie)<-[:DIRECTED]-(d1:Director),"
        " (a)-[:ACTED_IN]->(m2:Movie)<-[:DIRECTED]-(d2:Director)[/green]"
    )

    result = tx.run(
        """
        MATCH (d1:Director {name: 'Lana Wachowski'})-[:DIRECTED]->(m:Movie)<-[:ACTED_IN]-(a:Actor),
              (d2:Director {name: 'Lilly Wachowski'})-[:DIRECTED]->(m2:Movie)<-[:ACTED_IN]-(a)
        WHERE m = m2  // Same movie
        RETURN DISTINCT a.name AS actor
        ORDER BY actor
        """
    )

    console.print("  Actors who worked with both Wachowskis:")
    for record in result:
        console.print(f"    - {record['actor']}")

    # Find co-actors (actors who appeared in same movie)
    console.print("\n[dim]Find Keanu's co-actors:[/dim]")
    console.print(
        '[green]MATCH (keanu:Actor {name: "Keanu Reeves"})-[:ACTED_IN]->(m)<-[:ACTED_IN]-(coactor)[/green]'
    )

    result = tx.run(
        """
        MATCH (keanu:Actor {name: 'Keanu Reeves'})-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(coactor:Actor)
        WHERE keanu <> coactor
        RETURN DISTINCT coactor.name AS coactor, collect(m.title) AS movies
        ORDER BY coactor
        """
    )

    console.print("\n  Keanu's Co-Actors:")
    for record in result:
        console.print(f"    - {record['coactor']}: {', '.join(record['movies'])}")


def demo_optional_match(tx):
    """Demonstrate OPTIONAL MATCH for nullable patterns."""
    console.print("\n[bold cyan]5. OPTIONAL MATCH - Nullable Patterns[/bold cyan]")

    # Find movies and their directors (some movies may not have directors in our data)
    console.print("\n[dim]Find all movies with optional director:[/dim]")
    console.print("[green]MATCH (m:Movie) OPTIONAL MATCH (m)<-[:DIRECTED]-(d:Director)[/green]")

    result = tx.run(
        """
        MATCH (m:Movie)
        OPTIONAL MATCH (m)<-[:DIRECTED]-(d:Director)
        RETURN m.title AS movie, collect(d.name) AS directors
        ORDER BY m.title
        """
    )

    table = Table(title="Movies with Optional Directors")
    table.add_column("Movie")
    table.add_column("Directors")

    for record in result:
        directors = record["directors"]
        # Filter out None values (from unmatched OPTIONAL MATCH)
        directors = [d for d in directors if d is not None]
        table.add_row(record["movie"], ", ".join(directors) if directors else "[dim]No director data[/dim]")
    console.print(table)


def demo_pattern_comprehension(tx):
    """Demonstrate pattern comprehension for inline collection building."""
    console.print("\n[bold cyan]6. Pattern Comprehension[/bold cyan]")

    console.print("\n[dim]Use pattern comprehension to get actor's movies inline:[/dim]")
    console.print(
        "[green]MATCH (a:Actor) RETURN a.name, [(a)-[:ACTED_IN]->(m) | m.title] AS movies[/green]"
    )

    result = tx.run(
        """
        MATCH (a:Actor)
        RETURN a.name AS actor,
               [(a)-[r:ACTED_IN]->(m:Movie) | {title: m.title, role: r.role}] AS filmography
        ORDER BY a.name
        """
    )

    for record in result:
        console.print(f"\n  [bold]{record['actor']}[/bold]")
        for film in record["filmography"]:
            console.print(f"    - {film['title']} as {film['role']}")


def cleanup(tx):
    """Clean up all example data."""
    tx.run("MATCH (n:Movie) DETACH DELETE n")
    tx.run("MATCH (n:Actor) DETACH DELETE n")
    tx.run("MATCH (n:Director) DETACH DELETE n")


def main():
    """Run all pattern matching examples."""
    console.print(Panel.fit("[bold]Neo4j Cypher - Example 2: Pattern Matching[/bold]"))

    driver = get_driver()

    try:
        driver.verify_connectivity()
        console.print("[green]Connected to Neo4j![/green]")

        with driver.session() as session:
            # Setup test data
            session.execute_write(setup_movie_data)

            # Run demos
            session.execute_read(demo_basic_patterns)
            session.execute_read(demo_multiple_relationships)
            session.execute_read(demo_undirected_patterns)
            session.execute_read(demo_complex_patterns)
            session.execute_read(demo_optional_match)
            session.execute_read(demo_pattern_comprehension)

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
