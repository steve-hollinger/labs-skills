"""
Example 3: Duration and Date Arithmetic

This example demonstrates working with durations in Neo4j:
- Creating duration values
- Adding/subtracting durations from dates
- Calculating durations between dates
- Common date arithmetic patterns

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
    tx.run("MATCH (n:DurationExample) DETACH DELETE n")


def demo_create_durations(tx):
    """Demonstrate creating duration values."""
    console.print("\n[bold cyan]1. Creating Duration Values[/bold cyan]")

    # Create from components
    console.print("\n[dim]Create durations from components:[/dim]")
    console.print("[green]duration({days: 30}), duration({months: 1}), duration({hours: 24})[/green]")

    result = tx.run(
        """
        RETURN
            duration({days: 30}) AS thirtyDays,
            duration({months: 1}) AS oneMonth,
            duration({weeks: 2}) AS twoWeeks,
            duration({hours: 24}) AS twentyFourHours,
            duration({minutes: 90}) AS ninetyMinutes,
            duration({years: 1, months: 6}) AS yearAndHalf
        """
    )

    record = result.single()

    table = Table(title="Duration Values")
    table.add_column("Description")
    table.add_column("Duration")

    table.add_row("30 days", str(record["thirtyDays"]))
    table.add_row("1 month", str(record["oneMonth"]))
    table.add_row("2 weeks", str(record["twoWeeks"]))
    table.add_row("24 hours", str(record["twentyFourHours"]))
    table.add_row("90 minutes", str(record["ninetyMinutes"]))
    table.add_row("1 year 6 months", str(record["yearAndHalf"]))

    console.print(table)

    # ISO 8601 format
    console.print("\n[dim]Create duration from ISO 8601 format:[/dim]")
    console.print("[green]duration('P1Y2M3DT4H5M6S') - 1 year, 2 months, 3 days, 4 hours, 5 min, 6 sec[/green]")

    result = tx.run(
        """
        RETURN duration('P1Y2M3DT4H5M6S') AS iso,
               duration('P30D') AS thirtyDays,
               duration('PT24H') AS twentyFourHours
        """
    )

    record = result.single()
    console.print(f"  P1Y2M3DT4H5M6S = {record['iso']}")
    console.print(f"  P30D = {record['thirtyDays']}")
    console.print(f"  PT24H = {record['twentyFourHours']}")


def demo_add_subtract_durations(tx):
    """Demonstrate adding and subtracting durations."""
    console.print("\n[bold cyan]2. Adding and Subtracting Durations[/bold cyan]")

    console.print("\n[dim]Add duration to date:[/dim]")
    console.print('[green]date("2024-01-15") + duration({days: 30})[/green]')

    result = tx.run(
        """
        WITH date('2024-01-15') AS startDate
        RETURN startDate,
               startDate + duration({days: 30}) AS plus30Days,
               startDate + duration({months: 1}) AS plus1Month,
               startDate + duration({years: 1}) AS plus1Year
        """
    )

    record = result.single()

    table = Table(title="Adding Durations to 2024-01-15")
    table.add_column("Operation")
    table.add_column("Result")

    table.add_row("Start Date", str(record["startDate"]))
    table.add_row("+ 30 days", str(record["plus30Days"]))
    table.add_row("+ 1 month", str(record["plus1Month"]))
    table.add_row("+ 1 year", str(record["plus1Year"]))

    console.print(table)

    # Subtract duration
    console.print("\n[dim]Subtract duration from date:[/dim]")
    console.print('[green]date("2024-03-15") - duration({days: 30})[/green]')

    result = tx.run(
        """
        WITH date('2024-03-15') AS endDate
        RETURN endDate,
               endDate - duration({days: 30}) AS minus30Days,
               endDate - duration({months: 1}) AS minus1Month,
               endDate - duration({weeks: 2}) AS minus2Weeks
        """
    )

    record = result.single()

    table = Table(title="Subtracting Durations from 2024-03-15")
    table.add_column("Operation")
    table.add_column("Result")

    table.add_row("Start Date", str(record["endDate"]))
    table.add_row("- 30 days", str(record["minus30Days"]))
    table.add_row("- 1 month", str(record["minus1Month"]))
    table.add_row("- 2 weeks", str(record["minus2Weeks"]))

    console.print(table)


def demo_duration_between(tx):
    """Demonstrate calculating duration between dates."""
    console.print("\n[bold cyan]3. Duration Between Dates[/bold cyan]")

    console.print("\n[dim]Calculate duration between two dates:[/dim]")
    console.print('[green]duration.between(date("2024-01-01"), date("2024-12-31"))[/green]')

    result = tx.run(
        """
        WITH date('2024-01-01') AS start, date('2024-12-31') AS end
        RETURN start, end,
               duration.between(start, end) AS betweenDuration,
               duration.inDays(start, end) AS inDays,
               duration.inMonths(start, end) AS inMonths
        """
    )

    record = result.single()

    table = Table(title="Duration Between 2024-01-01 and 2024-12-31")
    table.add_column("Measure")
    table.add_column("Value")

    table.add_row("duration.between()", str(record["betweenDuration"]))
    table.add_row("duration.inDays()", str(record["inDays"]))
    table.add_row("duration.inMonths()", str(record["inMonths"]))

    console.print(table)

    # Get actual day count
    console.print("\n[dim]Extract actual day count:[/dim]")
    console.print("[green]duration.inDays(start, end).days[/green]")

    result = tx.run(
        """
        WITH date('2024-01-01') AS start, date('2024-12-31') AS end
        RETURN duration.inDays(start, end).days AS dayCount,
               duration.inMonths(start, end).months AS monthCount
        """
    )

    record = result.single()
    console.print(f"  Days: {record['dayCount']}")
    console.print(f"  Months: {record['monthCount']}")


def demo_common_patterns(tx):
    """Demonstrate common date arithmetic patterns."""
    console.print("\n[bold cyan]4. Common Date Arithmetic Patterns[/bold cyan]")

    # Recent events pattern
    console.print("\n[dim]Pattern: Find events in last N days[/dim]")
    console.print("[green]WHERE e.timestamp > datetime() - duration({days: 7})[/green]")

    # Create sample events
    tx.run(
        """
        CREATE (:DurationExample {name: 'Recent', timestamp: datetime() - duration({days: 2})})
        CREATE (:DurationExample {name: 'Older', timestamp: datetime() - duration({days: 10})})
        CREATE (:DurationExample {name: 'Ancient', timestamp: datetime() - duration({days: 30})})
        """
    )

    result = tx.run(
        """
        MATCH (e:DurationExample)
        WHERE e.timestamp > datetime() - duration({days: 7})
        RETURN e.name, e.timestamp
        """
    )

    console.print("  Events in last 7 days:")
    for record in result:
        console.print(f"    - {record['e.name']}")

    # Age calculation
    console.print("\n[dim]Pattern: Calculate age from birthdate[/dim]")
    console.print("[green]duration.between(p.birthDate, date()).years[/green]")

    tx.run(
        """
        CREATE (:DurationExample {name: 'Alice', birthDate: date('1990-05-15')})
        CREATE (:DurationExample {name: 'Bob', birthDate: date('1985-12-25')})
        """
    )

    result = tx.run(
        """
        MATCH (p:DurationExample)
        WHERE p.birthDate IS NOT NULL
        WITH p, duration.between(p.birthDate, date()) AS age
        RETURN p.name,
               p.birthDate,
               age.years AS years,
               age.monthsOfYear AS months,
               age.daysOfMonth AS days
        """
    )

    table = Table(title="Age Calculation")
    table.add_column("Name")
    table.add_column("Birth Date")
    table.add_column("Age")

    for record in result:
        age_str = f"{record['years']} years, {record['months']} months, {record['days']} days"
        table.add_row(record["p.name"], str(record["p.birthDate"]), age_str)

    console.print(table)

    # Deadline calculation
    console.print("\n[dim]Pattern: Calculate deadline from due date[/dim]")
    console.print("[green]duration.inDays(date(), t.dueDate).days[/green]")

    tx.run(
        """
        CREATE (:DurationExample {name: 'Task 1', dueDate: date() + duration({days: 5})})
        CREATE (:DurationExample {name: 'Task 2', dueDate: date() + duration({days: 14})})
        CREATE (:DurationExample {name: 'Overdue', dueDate: date() - duration({days: 3})})
        """
    )

    result = tx.run(
        """
        MATCH (t:DurationExample)
        WHERE t.dueDate IS NOT NULL
        WITH t, duration.inDays(date(), t.dueDate).days AS daysRemaining
        RETURN t.name, t.dueDate, daysRemaining,
               CASE
                   WHEN daysRemaining < 0 THEN 'OVERDUE'
                   WHEN daysRemaining <= 7 THEN 'SOON'
                   ELSE 'OK'
               END AS status
        ORDER BY daysRemaining
        """
    )

    table = Table(title="Task Deadlines")
    table.add_column("Task")
    table.add_column("Due Date")
    table.add_column("Days Remaining")
    table.add_column("Status")

    for record in result:
        table.add_row(
            record["t.name"],
            str(record["t.dueDate"]),
            str(record["daysRemaining"]),
            record["status"],
        )

    console.print(table)


def demo_month_arithmetic_gotchas(tx):
    """Demonstrate gotchas with month arithmetic."""
    console.print("\n[bold cyan]5. Month Arithmetic Gotchas[/bold cyan]")

    console.print("\n[dim]Adding months near month boundaries:[/dim]")

    result = tx.run(
        """
        WITH date('2024-01-31') AS jan31
        RETURN jan31,
               jan31 + duration({months: 1}) AS plusOneMonth,
               jan31 + duration({days: 30}) AS plus30Days,
               jan31 + duration({days: 31}) AS plus31Days
        """
    )

    record = result.single()

    table = Table(title="Adding Time to January 31, 2024")
    table.add_column("Operation")
    table.add_column("Result")
    table.add_column("Note")

    table.add_row(
        "Start",
        str(record["jan31"]),
        "January has 31 days"
    )
    table.add_row(
        "+ 1 month",
        str(record["plusOneMonth"]),
        "Feb 29 (2024 is leap year)"
    )
    table.add_row(
        "+ 30 days",
        str(record["plus30Days"]),
        "March 1"
    )
    table.add_row(
        "+ 31 days",
        str(record["plus31Days"]),
        "March 2"
    )

    console.print(table)

    console.print("\n[yellow]  Warning: Adding months doesn't always give predictable results!")
    console.print("  - January 31 + 1 month = February 29 (or 28 in non-leap year)")
    console.print("  - Use days when you need exact precision[/yellow]")


def main():
    """Run all duration examples."""
    console.print(Panel.fit("[bold]Neo4j DATE vs DATETIME - Example 3: Duration and Date Arithmetic[/bold]"))

    driver = get_driver()

    try:
        driver.verify_connectivity()
        console.print("[green]Connected to Neo4j![/green]")

        with driver.session() as session:
            # Clean up
            session.execute_write(cleanup)

            # Run demos
            session.execute_read(demo_create_durations)
            session.execute_read(demo_add_subtract_durations)
            session.execute_read(demo_duration_between)
            session.execute_write(demo_common_patterns)
            session.execute_read(demo_month_arithmetic_gotchas)

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
