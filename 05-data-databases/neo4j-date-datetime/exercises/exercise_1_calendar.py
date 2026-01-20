"""
Exercise 1: Event Calendar

Build and query an event calendar with proper date/time handling.

Tasks:
1. Create events with appropriate temporal types (DATE vs DATETIME)
2. Query events by date range
3. Find upcoming events
4. Group events by date

Instructions:
- Complete the TODO sections below
- Run with: python -m exercises.exercise_1_calendar
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
    """Create calendar event data."""
    tx.run("MATCH (n:CalEvent) DETACH DELETE n")

    # TODO: Create at least 6 events with:
    # - All-day events using DATE (conferences, holidays, birthdays)
    # - Timed events using DATETIME (meetings, calls)
    # Include events in the past, present (this week), and future

    pass  # Remove and add your code


def task1_events_this_week(tx) -> list[dict]:
    """
    Task 1: Find all events happening this week.

    Returns:
        List of events with name and date/time
    """
    # TODO: Query events where the date falls within the current week
    # Hint: Use date() and duration to calculate week boundaries

    query = """
    // TODO: Your query here
    RETURN '' AS name, date() AS eventDate
    """

    result = tx.run(query)
    return [{"name": r["name"], "date": r["eventDate"]} for r in result]


def task2_upcoming_events(tx, days: int = 30) -> list[dict]:
    """
    Task 2: Find events in the next N days.

    Args:
        days: Number of days to look ahead

    Returns:
        List of upcoming events with days until event
    """
    # TODO: Query events happening within the next N days
    # Include the number of days until each event

    query = """
    // TODO: Your query here
    RETURN '' AS name, 0 AS daysUntil
    """

    result = tx.run(query, days=days)
    return [{"name": r["name"], "daysUntil": r["daysUntil"]} for r in result]


def task3_events_by_month(tx, year: int) -> list[dict]:
    """
    Task 3: Group events by month for a given year.

    Args:
        year: The year to analyze

    Returns:
        List of months with event counts
    """
    # TODO: Group events by month and count them
    # Return month number and count

    query = """
    // TODO: Your query here
    RETURN 0 AS month, 0 AS count
    """

    result = tx.run(query, year=year)
    return [{"month": r["month"], "count": r["count"]} for r in result]


def main():
    console.print("[bold]Exercise 1: Event Calendar[/bold]\n")

    driver = get_driver()

    try:
        driver.verify_connectivity()

        with driver.session() as session:
            session.execute_write(setup_data)

            console.print("[cyan]Task 1: Events This Week[/cyan]")
            events = session.execute_read(task1_events_this_week)
            for e in events:
                console.print(f"  {e['name']}: {e['date']}")

            console.print("\n[cyan]Task 2: Upcoming Events (30 days)[/cyan]")
            upcoming = session.execute_read(task2_upcoming_events, 30)
            for e in upcoming:
                console.print(f"  {e['name']}: in {e['daysUntil']} days")

            console.print("\n[cyan]Task 3: Events by Month (2024)[/cyan]")
            monthly = session.execute_read(task3_events_by_month, 2024)
            for m in monthly:
                console.print(f"  Month {m['month']}: {m['count']} events")

            session.execute_write(lambda tx: tx.run("MATCH (n:CalEvent) DETACH DELETE n"))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise
    finally:
        driver.close()


if __name__ == "__main__":
    main()
