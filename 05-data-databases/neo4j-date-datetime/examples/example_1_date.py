"""
Example 1: DATE Basics

This example demonstrates working with the DATE type in Neo4j:
- Creating DATE values from strings and components
- Querying and filtering by date
- Extracting date components
- Date comparisons

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


def cleanup(tx):
    """Remove all example data."""
    tx.run("MATCH (n:DateExample) DETACH DELETE n")


def demo_create_dates(tx):
    """Demonstrate creating DATE values."""
    console.print("\n[bold cyan]1. Creating DATE Values[/bold cyan]")

    # Create from ISO string
    console.print("\n[dim]Create DATE from ISO string:[/dim]")
    console.print("[green]CREATE (p:DateExample {name: 'Alice', birthDate: date('1990-05-15')})[/green]")

    tx.run(
        """
        CREATE (p:DateExample {
            name: 'Alice',
            birthDate: date('1990-05-15')
        })
        """
    )
    console.print("  Created Alice with birthDate: 1990-05-15")

    # Create from components
    console.print("\n[dim]Create DATE from components:[/dim]")
    console.print(
        "[green]CREATE (p:DateExample {name: 'Bob', birthDate: date({year: 1985, month: 12, day: 25})})[/green]"
    )

    tx.run(
        """
        CREATE (p:DateExample {
            name: 'Bob',
            birthDate: date({year: 1985, month: 12, day: 25})
        })
        """
    )
    console.print("  Created Bob with birthDate: 1985-12-25")

    # Create with today's date
    console.print("\n[dim]Create with today's date:[/dim]")
    console.print("[green]CREATE (p:DateExample {name: 'Charlie', registrationDate: date()})[/green]")

    result = tx.run(
        """
        CREATE (p:DateExample {
            name: 'Charlie',
            registrationDate: date()
        })
        RETURN p.registrationDate AS regDate
        """
    )
    reg_date = result.single()["regDate"]
    console.print(f"  Created Charlie with registrationDate: {reg_date}")

    # Create more people for queries
    tx.run(
        """
        CREATE (:DateExample {name: 'Diana', birthDate: date('1995-03-20')})
        CREATE (:DateExample {name: 'Eve', birthDate: date('1990-08-10')})
        CREATE (:DateExample {name: 'Frank', birthDate: date('1988-01-01')})
        """
    )
    console.print("\n  Created Diana, Eve, and Frank with various dates")


def demo_query_dates(tx):
    """Demonstrate querying DATE values."""
    console.print("\n[bold cyan]2. Querying DATE Values[/bold cyan]")

    # Simple date query
    console.print("\n[dim]Find person by exact date:[/dim]")
    console.print(
        '[green]MATCH (p:DateExample {birthDate: date("1990-05-15")}) RETURN p.name[/green]'
    )

    result = tx.run(
        """
        MATCH (p:DateExample {birthDate: date('1990-05-15')})
        RETURN p.name AS name
        """
    )
    record = result.single()
    if record:
        console.print(f"  Found: {record['name']}")

    # Date comparison
    console.print("\n[dim]Find people born after 1990:[/dim]")
    console.print('[green]MATCH (p:DateExample) WHERE p.birthDate > date("1990-01-01")[/green]')

    result = tx.run(
        """
        MATCH (p:DateExample)
        WHERE p.birthDate > date('1990-01-01')
        RETURN p.name, p.birthDate
        ORDER BY p.birthDate
        """
    )

    for record in result:
        console.print(f"  {record['p.name']}: {record['p.birthDate']}")

    # Date range
    console.print("\n[dim]Find people born in the 1990s:[/dim]")
    console.print(
        '[green]WHERE date("1990-01-01") <= p.birthDate <= date("1999-12-31")[/green]'
    )

    result = tx.run(
        """
        MATCH (p:DateExample)
        WHERE date('1990-01-01') <= p.birthDate <= date('1999-12-31')
        RETURN p.name, p.birthDate
        ORDER BY p.birthDate
        """
    )

    for record in result:
        console.print(f"  {record['p.name']}: {record['p.birthDate']}")


def demo_extract_components(tx):
    """Demonstrate extracting date components."""
    console.print("\n[bold cyan]3. Extracting Date Components[/bold cyan]")

    console.print("\n[dim]Extract year, month, day from dates:[/dim]")
    console.print(
        "[green]RETURN p.birthDate.year, p.birthDate.month, p.birthDate.day[/green]"
    )

    result = tx.run(
        """
        MATCH (p:DateExample)
        WHERE p.birthDate IS NOT NULL
        RETURN p.name AS name,
               p.birthDate AS date,
               p.birthDate.year AS year,
               p.birthDate.month AS month,
               p.birthDate.day AS day,
               p.birthDate.dayOfWeek AS dayOfWeek,
               p.birthDate.dayOfYear AS dayOfYear
        ORDER BY p.birthDate
        """
    )

    table = Table(title="Date Components")
    table.add_column("Name")
    table.add_column("Date")
    table.add_column("Year")
    table.add_column("Month")
    table.add_column("Day")
    table.add_column("Day of Week")
    table.add_column("Day of Year")

    for record in result:
        table.add_row(
            record["name"],
            str(record["date"]),
            str(record["year"]),
            str(record["month"]),
            str(record["day"]),
            str(record["dayOfWeek"]),
            str(record["dayOfYear"]),
        )

    console.print(table)


def demo_group_by_date_components(tx):
    """Demonstrate grouping by date components."""
    console.print("\n[bold cyan]4. Grouping by Date Components[/bold cyan]")

    # Group by birth year
    console.print("\n[dim]Count people by birth year:[/dim]")
    console.print("[green]RETURN p.birthDate.year AS year, COUNT(p) AS count[/green]")

    result = tx.run(
        """
        MATCH (p:DateExample)
        WHERE p.birthDate IS NOT NULL
        RETURN p.birthDate.year AS year, COUNT(p) AS count
        ORDER BY year
        """
    )

    for record in result:
        console.print(f"  {record['year']}: {record['count']} people")

    # Group by birth month
    console.print("\n[dim]Count people by birth month:[/dim]")

    result = tx.run(
        """
        MATCH (p:DateExample)
        WHERE p.birthDate IS NOT NULL
        RETURN p.birthDate.month AS month, COLLECT(p.name) AS names
        ORDER BY month
        """
    )

    month_names = [
        "", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    for record in result:
        month_name = month_names[record["month"]]
        console.print(f"  {month_name}: {', '.join(record['names'])}")


def demo_date_vs_string(tx):
    """Demonstrate why DATE is better than strings."""
    console.print("\n[bold cyan]5. DATE vs String Comparison[/bold cyan]")

    # Create nodes with string dates (for comparison)
    tx.run(
        """
        CREATE (:DateExample {name: 'StringDate1', dateStr: '2024-01-15'})
        CREATE (:DateExample {name: 'StringDate2', dateStr: '2024-09-01'})
        CREATE (:DateExample {name: 'StringDate3', dateStr: '2024-10-01'})
        """
    )

    # Show string comparison problem
    console.print("\n[dim]String comparison (WRONG - lexicographic):[/dim]")
    console.print('[green]WHERE p.dateStr > "2024-09-01"[/green]')

    result = tx.run(
        """
        MATCH (p:DateExample)
        WHERE p.dateStr IS NOT NULL AND p.dateStr > '2024-09-01'
        RETURN p.name, p.dateStr
        ORDER BY p.dateStr
        """
    )

    console.print("  [yellow]Expected: 2024-10-01 only[/yellow]")
    console.print("  [red]Actual results (string comparison):[/red]")
    for record in result:
        console.print(f"    {record['p.name']}: {record['p.dateStr']}")

    # Correct way with DATE
    console.print("\n[dim]Correct comparison with DATE:[/dim]")
    console.print('[green]WHERE date(p.dateStr) > date("2024-09-01")[/green]')

    result = tx.run(
        """
        MATCH (p:DateExample)
        WHERE p.dateStr IS NOT NULL AND date(p.dateStr) > date('2024-09-01')
        RETURN p.name, p.dateStr
        ORDER BY date(p.dateStr)
        """
    )

    console.print("  [green]Correct results:[/green]")
    for record in result:
        console.print(f"    {record['p.name']}: {record['p.dateStr']}")


def main():
    """Run all DATE examples."""
    console.print(Panel.fit("[bold]Neo4j DATE vs DATETIME - Example 1: DATE Basics[/bold]"))

    driver = get_driver()

    try:
        driver.verify_connectivity()
        console.print("[green]Connected to Neo4j![/green]")

        with driver.session() as session:
            # Clean up
            session.execute_write(cleanup)

            # Run demos
            session.execute_write(demo_create_dates)
            session.execute_read(demo_query_dates)
            session.execute_read(demo_extract_components)
            session.execute_read(demo_group_by_date_components)
            session.execute_write(demo_date_vs_string)

            # Clean up
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
