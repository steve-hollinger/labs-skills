"""
Example 2: DATETIME and Timezones

This example demonstrates working with DATETIME in Neo4j:
- Creating DATETIME with timezones
- Timezone conversion
- DATETIME vs LOCALDATETIME
- Querying and filtering timestamps

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
    tx.run("MATCH (n:DateTimeExample) DETACH DELETE n")


def demo_create_datetime(tx):
    """Demonstrate creating DATETIME values."""
    console.print("\n[bold cyan]1. Creating DATETIME Values[/bold cyan]")

    # Create with UTC
    console.print("\n[dim]Create DATETIME with UTC (Z suffix):[/dim]")
    console.print(
        "[green]CREATE (e:DateTimeExample {timestamp: datetime('2024-03-15T14:30:00Z')})[/green]"
    )

    tx.run(
        """
        CREATE (e:DateTimeExample {
            name: 'UTC Event',
            timestamp: datetime('2024-03-15T14:30:00Z')
        })
        """
    )
    console.print("  Created event at 2024-03-15T14:30:00Z")

    # Create with timezone offset
    console.print("\n[dim]Create DATETIME with timezone offset:[/dim]")
    console.print(
        "[green]CREATE (e:DateTimeExample {timestamp: datetime('2024-03-15T14:30:00+05:30')})[/green]"
    )

    tx.run(
        """
        CREATE (e:DateTimeExample {
            name: 'India Event',
            timestamp: datetime('2024-03-15T14:30:00+05:30')
        })
        """
    )
    console.print("  Created event at 2024-03-15T14:30:00+05:30 (India Standard Time)")

    # Create with named timezone
    console.print("\n[dim]Create DATETIME with named timezone:[/dim]")
    console.print(
        "[green]datetime({year: 2024, month: 3, day: 15, hour: 14, minute: 30, timezone: 'America/New_York'})[/green]"
    )

    tx.run(
        """
        CREATE (e:DateTimeExample {
            name: 'New York Event',
            timestamp: datetime({
                year: 2024, month: 3, day: 15,
                hour: 14, minute: 30,
                timezone: 'America/New_York'
            })
        })
        """
    )
    console.print("  Created event at 2024-03-15T14:30:00 America/New_York")

    # Create with current timestamp
    console.print("\n[dim]Create DATETIME with current time:[/dim]")
    console.print("[green]CREATE (e:DateTimeExample {timestamp: datetime()})[/green]")

    result = tx.run(
        """
        CREATE (e:DateTimeExample {
            name: 'Now Event',
            timestamp: datetime()
        })
        RETURN e.timestamp AS ts
        """
    )
    console.print(f"  Created event at {result.single()['ts']}")


def demo_timezone_conversion(tx):
    """Demonstrate timezone conversion."""
    console.print("\n[bold cyan]2. Timezone Conversion[/bold cyan]")

    # Create a reference event in UTC
    tx.run(
        """
        MERGE (e:DateTimeExample {name: 'Reference Event'})
        SET e.timestamp = datetime('2024-03-15T12:00:00Z')
        """
    )

    console.print("\n[dim]Convert UTC timestamp to different timezones:[/dim]")
    console.print(
        "[green]datetime({datetime: e.timestamp, timezone: 'America/New_York'})[/green]"
    )

    result = tx.run(
        """
        MATCH (e:DateTimeExample {name: 'Reference Event'})
        RETURN e.timestamp AS utc,
               datetime({datetime: e.timestamp, timezone: 'America/New_York'}) AS newYork,
               datetime({datetime: e.timestamp, timezone: 'Europe/London'}) AS london,
               datetime({datetime: e.timestamp, timezone: 'Asia/Tokyo'}) AS tokyo,
               datetime({datetime: e.timestamp, timezone: 'Australia/Sydney'}) AS sydney
        """
    )

    record = result.single()

    table = Table(title="Same Moment in Different Timezones")
    table.add_column("Timezone")
    table.add_column("Local Time")

    table.add_row("UTC", str(record["utc"]))
    table.add_row("New York (EST/EDT)", str(record["newYork"]))
    table.add_row("London (GMT/BST)", str(record["london"]))
    table.add_row("Tokyo (JST)", str(record["tokyo"]))
    table.add_row("Sydney (AEST/AEDT)", str(record["sydney"]))

    console.print(table)


def demo_datetime_vs_localdatetime(tx):
    """Demonstrate DATETIME vs LOCALDATETIME."""
    console.print("\n[bold cyan]3. DATETIME vs LOCALDATETIME[/bold cyan]")

    # Create both types
    console.print("\n[dim]Create events with DATETIME and LOCALDATETIME:[/dim]")

    tx.run(
        """
        // DATETIME - specific moment in time
        CREATE (e1:DateTimeExample {
            name: 'Global Meeting',
            type: 'datetime',
            timestamp: datetime('2024-03-15T14:30:00Z')
        })

        // LOCALDATETIME - wall clock time, no timezone
        CREATE (e2:DateTimeExample {
            name: 'Local Lunch',
            type: 'localdatetime',
            localTimestamp: localdatetime('2024-03-15T12:00:00')
        })
        """
    )

    # Show the difference
    result = tx.run(
        """
        MATCH (e:DateTimeExample)
        WHERE e.type IN ['datetime', 'localdatetime']
        RETURN e.name AS name,
               e.type AS type,
               e.timestamp AS dt,
               e.localTimestamp AS ldt
        """
    )

    console.print("\n  [bold]Key Differences:[/bold]")
    console.print("  DATETIME:")
    console.print("    - Represents a specific instant in time")
    console.print("    - Has timezone information (explicit or implicit)")
    console.print("    - Use for: events, logs, timestamps that need global consistency")
    console.print("\n  LOCALDATETIME:")
    console.print("    - Represents wall clock time without timezone")
    console.print("    - No timezone conversion possible")
    console.print("    - Use for: local events, schedules where timezone is implicit")

    table = Table(title="DATETIME vs LOCALDATETIME")
    table.add_column("Event")
    table.add_column("Type")
    table.add_column("Value")

    for record in result:
        value = str(record["dt"]) if record["dt"] else str(record["ldt"])
        table.add_row(record["name"], record["type"], value)

    console.print(table)


def demo_query_datetime(tx):
    """Demonstrate querying DATETIME values."""
    console.print("\n[bold cyan]4. Querying DATETIME Values[/bold cyan]")

    # Create some events
    tx.run(
        """
        CREATE (:DateTimeExample {name: 'Event A', timestamp: datetime('2024-01-15T10:00:00Z')})
        CREATE (:DateTimeExample {name: 'Event B', timestamp: datetime('2024-03-15T14:00:00Z')})
        CREATE (:DateTimeExample {name: 'Event C', timestamp: datetime('2024-06-15T18:00:00Z')})
        CREATE (:DateTimeExample {name: 'Event D', timestamp: datetime('2024-12-15T22:00:00Z')})
        """
    )

    # Query by exact timestamp
    console.print("\n[dim]Find events after a specific datetime:[/dim]")
    console.print('[green]WHERE e.timestamp > datetime("2024-03-01T00:00:00Z")[/green]')

    result = tx.run(
        """
        MATCH (e:DateTimeExample)
        WHERE e.timestamp > datetime('2024-03-01T00:00:00Z')
        RETURN e.name, e.timestamp
        ORDER BY e.timestamp
        """
    )

    for record in result:
        console.print(f"  {record['e.name']}: {record['e.timestamp']}")

    # Query by date part
    console.print("\n[dim]Find events on a specific date (ignoring time):[/dim]")
    console.print('[green]WHERE date(e.timestamp) = date("2024-03-15")[/green]')

    result = tx.run(
        """
        MATCH (e:DateTimeExample)
        WHERE date(e.timestamp) = date('2024-03-15')
        RETURN e.name, e.timestamp
        """
    )

    for record in result:
        console.print(f"  {record['e.name']}: {record['e.timestamp']}")

    # Query by hour
    console.print("\n[dim]Find events at specific hours:[/dim]")
    console.print("[green]WHERE e.timestamp.hour >= 14[/green]")

    result = tx.run(
        """
        MATCH (e:DateTimeExample)
        WHERE e.timestamp IS NOT NULL AND e.timestamp.hour >= 14
        RETURN e.name, e.timestamp.hour AS hour
        ORDER BY hour
        """
    )

    for record in result:
        console.print(f"  {record['e.name']}: hour {record['hour']}")


def demo_datetime_components(tx):
    """Demonstrate extracting DATETIME components."""
    console.print("\n[bold cyan]5. DATETIME Components[/bold cyan]")

    result = tx.run(
        """
        WITH datetime('2024-03-15T14:30:45.123456789Z') AS dt
        RETURN dt,
               dt.year AS year,
               dt.month AS month,
               dt.day AS day,
               dt.hour AS hour,
               dt.minute AS minute,
               dt.second AS second,
               dt.millisecond AS ms,
               dt.microsecond AS us,
               dt.nanosecond AS ns,
               dt.timezone AS tz,
               dt.offset AS offset,
               dt.epochMillis AS epochMs
        """
    )

    record = result.single()

    table = Table(title="DATETIME Components")
    table.add_column("Component")
    table.add_column("Value")

    table.add_row("Full Value", str(record["dt"]))
    table.add_row("Year", str(record["year"]))
    table.add_row("Month", str(record["month"]))
    table.add_row("Day", str(record["day"]))
    table.add_row("Hour", str(record["hour"]))
    table.add_row("Minute", str(record["minute"]))
    table.add_row("Second", str(record["second"]))
    table.add_row("Millisecond", str(record["ms"]))
    table.add_row("Microsecond", str(record["us"]))
    table.add_row("Nanosecond", str(record["ns"]))
    table.add_row("Timezone", str(record["tz"]))
    table.add_row("Offset", str(record["offset"]))
    table.add_row("Epoch Millis", str(record["epochMs"]))

    console.print(table)


def main():
    """Run all DATETIME examples."""
    console.print(Panel.fit("[bold]Neo4j DATE vs DATETIME - Example 2: DATETIME and Timezones[/bold]"))

    driver = get_driver()

    try:
        driver.verify_connectivity()
        console.print("[green]Connected to Neo4j![/green]")

        with driver.session() as session:
            # Clean up
            session.execute_write(cleanup)

            # Run demos
            session.execute_write(demo_create_datetime)
            session.execute_read(demo_timezone_conversion)
            session.execute_write(demo_datetime_vs_localdatetime)
            session.execute_write(demo_query_datetime)
            session.execute_read(demo_datetime_components)

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
