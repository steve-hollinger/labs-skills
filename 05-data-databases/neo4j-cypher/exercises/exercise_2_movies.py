"""
Exercise 2: Movie Database Queries

Build and query a movie database with actors, directors, and genres.

Tasks:
1. Create a movie database with actors, directors, movies, and genres
2. Write queries to find:
   - All movies by a specific actor
   - Actors who have worked together
   - Directors and their average movie rating
   - Movies by genre with actor count

Instructions:
- Complete the TODO sections below
- Run with: python -m exercises.exercise_2_movies
- Check your answers against exercises/solutions/solution_2.py
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
    """Create the movie database."""
    # Clean up
    tx.run("MATCH (n:ExMovie) DETACH DELETE n")
    tx.run("MATCH (n:ExActor) DETACH DELETE n")
    tx.run("MATCH (n:ExDirector) DETACH DELETE n")
    tx.run("MATCH (n:ExGenre) DETACH DELETE n")

    # TODO: Create a movie database with:
    # - At least 5 movies with title, year, and rating properties
    # - At least 6 actors with name property
    # - At least 2 directors with name property
    # - At least 3 genres with name property
    #
    # Create relationships:
    # - ACTED_IN (actor to movie) with 'role' property
    # - DIRECTED (director to movie)
    # - HAS_GENRE (movie to genre)
    #
    # Make sure some actors appear in multiple movies
    # Make sure some movies have multiple actors

    pass  # Remove this and add your code


def task1_movies_by_actor(tx, actor_name: str) -> list[dict]:
    """
    Task 1: Find all movies by a specific actor.

    Args:
        actor_name: Name of the actor

    Returns:
        List of dicts with 'title', 'year', 'role'
    """
    # TODO: Write a query to find all movies an actor ACTED_IN
    # Include the role they played

    query = """
    // TODO: Your query here
    RETURN '' AS title, 0 AS year, '' AS role
    """

    result = tx.run(query, actor_name=actor_name)
    return [{"title": r["title"], "year": r["year"], "role": r["role"]} for r in result]


def task2_coactors(tx, actor_name: str) -> list[dict]:
    """
    Task 2: Find actors who have worked with a specific actor.

    Args:
        actor_name: Name of the actor

    Returns:
        List of dicts with 'coactor' name and 'movies' they worked together on
    """
    # TODO: Write a query to find co-actors (actors who appeared in the same movie)
    # Group by co-actor and collect the movies they worked together on
    # Exclude the actor themselves

    query = """
    // TODO: Your query here
    RETURN '' AS coactor, [] AS movies
    """

    result = tx.run(query, actor_name=actor_name)
    return [{"coactor": r["coactor"], "movies": r["movies"]} for r in result]


def task3_director_ratings(tx) -> list[dict]:
    """
    Task 3: Find average movie rating per director.

    Returns:
        List of dicts with 'director' name, 'avgRating', and 'movieCount'
    """
    # TODO: Write a query to calculate average rating per director
    # Also include the count of movies directed
    # Order by average rating descending

    query = """
    // TODO: Your query here
    RETURN '' AS director, 0.0 AS avgRating, 0 AS movieCount
    """

    result = tx.run(query)
    return [
        {
            "director": r["director"],
            "avgRating": r["avgRating"],
            "movieCount": r["movieCount"],
        }
        for r in result
    ]


def task4_genre_analysis(tx) -> list[dict]:
    """
    Task 4: Analyze movies by genre.

    Returns:
        List of dicts with 'genre', 'movieCount', 'avgActors'
    """
    # TODO: Write a query to:
    # - Group movies by genre
    # - Count movies per genre
    # - Calculate average number of actors per movie in each genre
    # Order by movie count descending

    query = """
    // TODO: Your query here
    RETURN '' AS genre, 0 AS movieCount, 0.0 AS avgActors
    """

    result = tx.run(query)
    return [
        {
            "genre": r["genre"],
            "movieCount": r["movieCount"],
            "avgActors": r["avgActors"],
        }
        for r in result
    ]


def main():
    console.print("[bold]Exercise 2: Movie Database Queries[/bold]\n")

    driver = get_driver()

    try:
        driver.verify_connectivity()

        with driver.session() as session:
            # Setup data
            session.execute_write(setup_data)

            # Run tasks
            console.print("[cyan]Task 1: Movies by Actor[/cyan]")
            movies = session.execute_read(task1_movies_by_actor, "Tom Hanks")  # Use your actor name
            for m in movies:
                console.print(f"  {m['title']} ({m['year']}) as {m['role']}")

            console.print("\n[cyan]Task 2: Co-Actors[/cyan]")
            coactors = session.execute_read(task2_coactors, "Tom Hanks")
            for c in coactors:
                console.print(f"  {c['coactor']}: {', '.join(c['movies'])}")

            console.print("\n[cyan]Task 3: Director Ratings[/cyan]")
            ratings = session.execute_read(task3_director_ratings)
            for r in ratings:
                console.print(
                    f"  {r['director']}: {r['avgRating']:.1f} avg ({r['movieCount']} movies)"
                )

            console.print("\n[cyan]Task 4: Genre Analysis[/cyan]")
            genres = session.execute_read(task4_genre_analysis)
            for g in genres:
                console.print(
                    f"  {g['genre']}: {g['movieCount']} movies, {g['avgActors']:.1f} avg actors"
                )

            # Cleanup
            session.execute_write(lambda tx: tx.run("MATCH (n:ExMovie) DETACH DELETE n"))
            session.execute_write(lambda tx: tx.run("MATCH (n:ExActor) DETACH DELETE n"))
            session.execute_write(lambda tx: tx.run("MATCH (n:ExDirector) DETACH DELETE n"))
            session.execute_write(lambda tx: tx.run("MATCH (n:ExGenre) DETACH DELETE n"))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise

    finally:
        driver.close()


if __name__ == "__main__":
    main()
