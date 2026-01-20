"""
Solution 2: Movie Database Queries

Complete solution for Exercise 2.
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

    # Create genres
    tx.run(
        """
        CREATE (:ExGenre {name: 'Drama'})
        CREATE (:ExGenre {name: 'Action'})
        CREATE (:ExGenre {name: 'Comedy'})
        """
    )

    # Create directors
    tx.run(
        """
        CREATE (:ExDirector {name: 'Steven Spielberg'})
        CREATE (:ExDirector {name: 'Christopher Nolan'})
        """
    )

    # Create actors
    tx.run(
        """
        CREATE (:ExActor {name: 'Tom Hanks'})
        CREATE (:ExActor {name: 'Leonardo DiCaprio'})
        CREATE (:ExActor {name: 'Matt Damon'})
        CREATE (:ExActor {name: 'Christian Bale'})
        CREATE (:ExActor {name: 'Anne Hathaway'})
        CREATE (:ExActor {name: 'Meg Ryan'})
        """
    )

    # Create movies
    tx.run(
        """
        CREATE (:ExMovie {title: 'Saving Private Ryan', year: 1998, rating: 8.6})
        CREATE (:ExMovie {title: 'Catch Me If You Can', year: 2002, rating: 8.1})
        CREATE (:ExMovie {title: 'The Dark Knight', year: 2008, rating: 9.0})
        CREATE (:ExMovie {title: 'Inception', year: 2010, rating: 8.8})
        CREATE (:ExMovie {title: 'Interstellar', year: 2014, rating: 8.6})
        """
    )

    # Connect movies to genres
    tx.run(
        """
        MATCH (m:ExMovie {title: 'Saving Private Ryan'}), (g:ExGenre {name: 'Drama'})
        CREATE (m)-[:HAS_GENRE]->(g)
        """
    )
    tx.run(
        """
        MATCH (m:ExMovie {title: 'Saving Private Ryan'}), (g:ExGenre {name: 'Action'})
        CREATE (m)-[:HAS_GENRE]->(g)
        """
    )
    tx.run(
        """
        MATCH (m:ExMovie {title: 'Catch Me If You Can'}), (g:ExGenre {name: 'Drama'})
        CREATE (m)-[:HAS_GENRE]->(g)
        """
    )
    tx.run(
        """
        MATCH (m:ExMovie {title: 'The Dark Knight'}), (g:ExGenre {name: 'Action'})
        CREATE (m)-[:HAS_GENRE]->(g)
        """
    )
    tx.run(
        """
        MATCH (m:ExMovie {title: 'Inception'}), (g:ExGenre {name: 'Action'})
        CREATE (m)-[:HAS_GENRE]->(g)
        """
    )
    tx.run(
        """
        MATCH (m:ExMovie {title: 'Interstellar'}), (g:ExGenre {name: 'Drama'})
        CREATE (m)-[:HAS_GENRE]->(g)
        """
    )

    # Connect directors to movies
    tx.run(
        """
        MATCH (d:ExDirector {name: 'Steven Spielberg'}), (m:ExMovie)
        WHERE m.title IN ['Saving Private Ryan', 'Catch Me If You Can']
        CREATE (d)-[:DIRECTED]->(m)
        """
    )
    tx.run(
        """
        MATCH (d:ExDirector {name: 'Christopher Nolan'}), (m:ExMovie)
        WHERE m.title IN ['The Dark Knight', 'Inception', 'Interstellar']
        CREATE (d)-[:DIRECTED]->(m)
        """
    )

    # Connect actors to movies
    tx.run(
        """
        MATCH (a:ExActor {name: 'Tom Hanks'}), (m:ExMovie {title: 'Saving Private Ryan'})
        CREATE (a)-[:ACTED_IN {role: 'Captain Miller'}]->(m)
        """
    )
    tx.run(
        """
        MATCH (a:ExActor {name: 'Tom Hanks'}), (m:ExMovie {title: 'Catch Me If You Can'})
        CREATE (a)-[:ACTED_IN {role: 'Carl Hanratty'}]->(m)
        """
    )
    tx.run(
        """
        MATCH (a:ExActor {name: 'Leonardo DiCaprio'}), (m:ExMovie {title: 'Catch Me If You Can'})
        CREATE (a)-[:ACTED_IN {role: 'Frank Abagnale Jr.'}]->(m)
        """
    )
    tx.run(
        """
        MATCH (a:ExActor {name: 'Leonardo DiCaprio'}), (m:ExMovie {title: 'Inception'})
        CREATE (a)-[:ACTED_IN {role: 'Dom Cobb'}]->(m)
        """
    )
    tx.run(
        """
        MATCH (a:ExActor {name: 'Matt Damon'}), (m:ExMovie {title: 'Saving Private Ryan'})
        CREATE (a)-[:ACTED_IN {role: 'Private Ryan'}]->(m)
        """
    )
    tx.run(
        """
        MATCH (a:ExActor {name: 'Matt Damon'}), (m:ExMovie {title: 'Interstellar'})
        CREATE (a)-[:ACTED_IN {role: 'Dr. Mann'}]->(m)
        """
    )
    tx.run(
        """
        MATCH (a:ExActor {name: 'Christian Bale'}), (m:ExMovie {title: 'The Dark Knight'})
        CREATE (a)-[:ACTED_IN {role: 'Bruce Wayne'}]->(m)
        """
    )
    tx.run(
        """
        MATCH (a:ExActor {name: 'Anne Hathaway'}), (m:ExMovie {title: 'The Dark Knight'})
        CREATE (a)-[:ACTED_IN {role: 'Catwoman'}]->(m)
        """
    )
    tx.run(
        """
        MATCH (a:ExActor {name: 'Anne Hathaway'}), (m:ExMovie {title: 'Interstellar'})
        CREATE (a)-[:ACTED_IN {role: 'Dr. Brand'}]->(m)
        """
    )

    console.print("[green]Created movie database[/green]")


def task1_movies_by_actor(tx, actor_name: str) -> list[dict]:
    """
    Task 1: Find all movies by a specific actor.

    Solution: Match ACTED_IN relationship and return movie details with role.
    """
    query = """
    MATCH (a:ExActor {name: $actor_name})-[r:ACTED_IN]->(m:ExMovie)
    RETURN m.title AS title, m.year AS year, r.role AS role
    ORDER BY m.year DESC
    """

    result = tx.run(query, actor_name=actor_name)
    return [{"title": r["title"], "year": r["year"], "role": r["role"]} for r in result]


def task2_coactors(tx, actor_name: str) -> list[dict]:
    """
    Task 2: Find actors who have worked with a specific actor.

    Solution: Find actors who ACTED_IN the same movies, group by co-actor.
    """
    query = """
    MATCH (actor:ExActor {name: $actor_name})-[:ACTED_IN]->(m:ExMovie)<-[:ACTED_IN]-(coactor:ExActor)
    WHERE actor <> coactor
    RETURN coactor.name AS coactor, COLLECT(DISTINCT m.title) AS movies
    ORDER BY coactor
    """

    result = tx.run(query, actor_name=actor_name)
    return [{"coactor": r["coactor"], "movies": r["movies"]} for r in result]


def task3_director_ratings(tx) -> list[dict]:
    """
    Task 3: Find average movie rating per director.

    Solution: Match directors to their movies and aggregate ratings.
    """
    query = """
    MATCH (d:ExDirector)-[:DIRECTED]->(m:ExMovie)
    RETURN d.name AS director,
           round(AVG(m.rating) * 10) / 10 AS avgRating,
           COUNT(m) AS movieCount
    ORDER BY avgRating DESC
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

    Solution: Group movies by genre, count movies, calculate average actors per movie.
    """
    query = """
    MATCH (m:ExMovie)-[:HAS_GENRE]->(g:ExGenre)
    OPTIONAL MATCH (a:ExActor)-[:ACTED_IN]->(m)
    WITH g, m, COUNT(DISTINCT a) AS actorCount
    RETURN g.name AS genre,
           COUNT(DISTINCT m) AS movieCount,
           round(AVG(actorCount) * 10) / 10 AS avgActors
    ORDER BY movieCount DESC
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
    console.print("[bold]Solution 2: Movie Database Queries[/bold]\n")

    driver = get_driver()

    try:
        driver.verify_connectivity()

        with driver.session() as session:
            # Setup data
            session.execute_write(setup_data)

            # Task 1
            console.print("[cyan]Task 1: Movies by Tom Hanks[/cyan]")
            movies = session.execute_read(task1_movies_by_actor, "Tom Hanks")
            for m in movies:
                console.print(f"  {m['title']} ({m['year']}) as {m['role']}")

            # Task 2
            console.print("\n[cyan]Task 2: Tom Hanks' Co-Actors[/cyan]")
            coactors = session.execute_read(task2_coactors, "Tom Hanks")
            for c in coactors:
                console.print(f"  {c['coactor']}: {', '.join(c['movies'])}")

            # Task 3
            console.print("\n[cyan]Task 3: Director Ratings[/cyan]")
            ratings = session.execute_read(task3_director_ratings)
            for r in ratings:
                console.print(
                    f"  {r['director']}: {r['avgRating']:.1f} avg ({r['movieCount']} movies)"
                )

            # Task 4
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

        console.print("\n[bold green]Solution completed![/bold green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise

    finally:
        driver.close()


if __name__ == "__main__":
    main()
