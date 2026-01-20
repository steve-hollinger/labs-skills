"""
Solution 1: Event Calendar

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
    """Create calendar event data."""
    tx.run("MATCH (n:CalEvent) DETACH DELETE n")

    # All-day events using DATE
    tx.run("""
        CREATE (:CalEvent {name: 'Team Building Day', eventDate: date() + duration({days: 3}), allDay: true})
        CREATE (:CalEvent {name: 'Company Holiday', eventDate: date() + duration({days: 10}), allDay: true})
        CREATE (:CalEvent {name: 'Q1 Review', eventDate: date() + duration({days: 25}), allDay: true})
        CREATE (:CalEvent {name: 'Past Conference', eventDate: date() - duration({days: 15}), allDay: true})
    """)

    # Timed events using DATETIME
    tx.run("""
        CREATE (:CalEvent {name: 'Morning Standup', eventDateTime: datetime() + duration({days: 1, hours: 9}), allDay: false})
        CREATE (:CalEvent {name: 'Client Call', eventDateTime: datetime() + duration({days: 5, hours: 14}), allDay: false})
        CREATE (:CalEvent {name: 'Sprint Planning', eventDateTime: datetime() + duration({days: 7, hours: 10}), allDay: false})
    """)

    console.print("[green]Created calendar events[/green]")


def task1_events_this_week(tx) -> list[dict]:
    """
    Task 1: Find all events happening this week.

    Solution: Calculate week boundaries and query events within range.
    """
    query = """
    WITH date() AS today,
         date() - duration({days: date().dayOfWeek - 1}) AS weekStart,
         date() + duration({days: 7 - date().dayOfWeek}) AS weekEnd
    MATCH (e:CalEvent)
    WHERE (e.eventDate IS NOT NULL AND weekStart <= e.eventDate <= weekEnd)
       OR (e.eventDateTime IS NOT NULL AND weekStart <= date(e.eventDateTime) <= weekEnd)
    RETURN e.name AS name,
           COALESCE(e.eventDate, date(e.eventDateTime)) AS eventDate
    ORDER BY eventDate
    """

    result = tx.run(query)
    return [{"name": r["name"], "date": r["eventDate"]} for r in result]


def task2_upcoming_events(tx, days: int = 30) -> list[dict]:
    """
    Task 2: Find events in the next N days.

    Solution: Filter by date range and calculate days until event.
    """
    query = """
    WITH date() AS today
    MATCH (e:CalEvent)
    WITH e, today,
         COALESCE(e.eventDate, date(e.eventDateTime)) AS eventDate
    WHERE eventDate >= today AND eventDate <= today + duration({days: $days})
    RETURN e.name AS name,
           duration.inDays(today, eventDate).days AS daysUntil
    ORDER BY daysUntil
    """

    result = tx.run(query, days=days)
    return [{"name": r["name"], "daysUntil": r["daysUntil"]} for r in result]


def task3_events_by_month(tx, year: int) -> list[dict]:
    """
    Task 3: Group events by month for a given year.

    Solution: Extract month from date and group with count.
    """
    query = """
    MATCH (e:CalEvent)
    WITH e, COALESCE(e.eventDate, date(e.eventDateTime)) AS eventDate
    WHERE eventDate.year = $year
    RETURN eventDate.month AS month, COUNT(e) AS count
    ORDER BY month
    """

    result = tx.run(query, year=year)
    return [{"month": r["month"], "count": r["count"]} for r in result]


def main():
    console.print("[bold]Solution 1: Event Calendar[/bold]\n")

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

            console.print("\n[cyan]Task 3: Events by Month (current year)[/cyan]")
            from datetime import date
            monthly = session.execute_read(task3_events_by_month, date.today().year)
            for m in monthly:
                console.print(f"  Month {m['month']}: {m['count']} events")

            session.execute_write(lambda tx: tx.run("MATCH (n:CalEvent) DETACH DELETE n"))

        console.print("\n[bold green]Solution completed![/bold green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise
    finally:
        driver.close()


if __name__ == "__main__":
    main()
