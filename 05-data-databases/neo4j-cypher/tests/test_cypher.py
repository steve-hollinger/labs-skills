"""
Tests for Neo4j Cypher skill.

These tests require Neo4j to be running.
Run with: make test-integration

To skip integration tests: make test-unit
"""

import os

import pytest
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable


def get_driver():
    """Create a Neo4j driver from environment variables."""
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    return GraphDatabase.driver(uri, auth=(user, password))


@pytest.fixture(scope="module")
def driver():
    """Provide a Neo4j driver for tests."""
    driver = get_driver()
    try:
        driver.verify_connectivity()
        yield driver
    except ServiceUnavailable:
        pytest.skip("Neo4j not available")
    finally:
        driver.close()


@pytest.fixture(scope="function")
def clean_db(driver):
    """Clean up test data before and after each test."""
    def cleanup():
        with driver.session() as session:
            session.run("MATCH (n:TestNode) DETACH DELETE n")
            session.run("MATCH (n:TestPerson) DETACH DELETE n")

    cleanup()
    yield
    cleanup()


class TestBasicCRUD:
    """Test basic CRUD operations."""

    @pytest.mark.integration
    def test_create_node(self, driver, clean_db):
        """Test creating a node with properties."""
        with driver.session() as session:
            result = session.run(
                """
                CREATE (n:TestNode {name: 'Test', value: 42})
                RETURN n.name AS name, n.value AS value
                """
            )
            record = result.single()

            assert record["name"] == "Test"
            assert record["value"] == 42

    @pytest.mark.integration
    def test_match_node(self, driver, clean_db):
        """Test matching existing nodes."""
        with driver.session() as session:
            # Create test data
            session.run("CREATE (:TestNode {name: 'Alpha'})")
            session.run("CREATE (:TestNode {name: 'Beta'})")

            # Match and count
            result = session.run("MATCH (n:TestNode) RETURN count(n) AS count")
            assert result.single()["count"] == 2

    @pytest.mark.integration
    def test_update_properties(self, driver, clean_db):
        """Test updating node properties with SET."""
        with driver.session() as session:
            # Create node
            session.run("CREATE (:TestNode {name: 'Original', version: 1})")

            # Update
            session.run(
                """
                MATCH (n:TestNode {name: 'Original'})
                SET n.version = 2, n.updated = true
                """
            )

            # Verify
            result = session.run(
                "MATCH (n:TestNode {name: 'Original'}) RETURN n.version, n.updated"
            )
            record = result.single()
            assert record["n.version"] == 2
            assert record["n.updated"] is True

    @pytest.mark.integration
    def test_delete_node(self, driver, clean_db):
        """Test deleting nodes."""
        with driver.session() as session:
            # Create
            session.run("CREATE (:TestNode {name: 'ToDelete'})")

            # Delete
            session.run("MATCH (n:TestNode {name: 'ToDelete'}) DELETE n")

            # Verify gone
            result = session.run(
                "MATCH (n:TestNode {name: 'ToDelete'}) RETURN count(n) AS count"
            )
            assert result.single()["count"] == 0

    @pytest.mark.integration
    def test_merge_creates_if_not_exists(self, driver, clean_db):
        """Test MERGE creates node if it doesn't exist."""
        with driver.session() as session:
            # MERGE on non-existent node
            result = session.run(
                """
                MERGE (n:TestNode {name: 'Merged'})
                ON CREATE SET n.created = true
                ON MATCH SET n.matched = true
                RETURN n.created, n.matched
                """
            )
            record = result.single()
            assert record["n.created"] is True
            assert record["n.matched"] is None

    @pytest.mark.integration
    def test_merge_matches_existing(self, driver, clean_db):
        """Test MERGE matches existing node."""
        with driver.session() as session:
            # Create first
            session.run("CREATE (:TestNode {name: 'Existing'})")

            # MERGE should match
            result = session.run(
                """
                MERGE (n:TestNode {name: 'Existing'})
                ON CREATE SET n.created = true
                ON MATCH SET n.matched = true
                RETURN n.created, n.matched
                """
            )
            record = result.single()
            assert record["n.created"] is None
            assert record["n.matched"] is True


class TestRelationships:
    """Test relationship operations."""

    @pytest.mark.integration
    def test_create_relationship(self, driver, clean_db):
        """Test creating relationships between nodes."""
        with driver.session() as session:
            # Create nodes and relationship
            session.run(
                """
                CREATE (a:TestPerson {name: 'Alice'})
                CREATE (b:TestPerson {name: 'Bob'})
                CREATE (a)-[:KNOWS {since: 2020}]->(b)
                """
            )

            # Verify
            result = session.run(
                """
                MATCH (a:TestPerson)-[r:KNOWS]->(b:TestPerson)
                RETURN a.name, r.since, b.name
                """
            )
            record = result.single()
            assert record["a.name"] == "Alice"
            assert record["r.since"] == 2020
            assert record["b.name"] == "Bob"

    @pytest.mark.integration
    def test_match_undirected(self, driver, clean_db):
        """Test undirected relationship matching."""
        with driver.session() as session:
            session.run(
                """
                CREATE (a:TestPerson {name: 'Alice'})
                CREATE (b:TestPerson {name: 'Bob'})
                CREATE (a)-[:KNOWS]->(b)
                """
            )

            # Undirected match should find from both sides
            result = session.run(
                """
                MATCH (p:TestPerson {name: 'Bob'})-[:KNOWS]-(other)
                RETURN other.name
                """
            )
            assert result.single()["other.name"] == "Alice"

    @pytest.mark.integration
    def test_detach_delete(self, driver, clean_db):
        """Test DETACH DELETE removes node and relationships."""
        with driver.session() as session:
            # Create connected nodes
            session.run(
                """
                CREATE (a:TestPerson {name: 'ToDelete'})
                CREATE (b:TestPerson {name: 'Connected'})
                CREATE (a)-[:KNOWS]->(b)
                """
            )

            # Delete with DETACH
            session.run("MATCH (n:TestPerson {name: 'ToDelete'}) DETACH DELETE n")

            # Verify node is gone
            result = session.run(
                "MATCH (n:TestPerson {name: 'ToDelete'}) RETURN count(n)"
            )
            assert result.single()["count(n)"] == 0

            # Connected node should still exist
            result = session.run(
                "MATCH (n:TestPerson {name: 'Connected'}) RETURN count(n)"
            )
            assert result.single()["count(n)"] == 1


class TestAggregations:
    """Test aggregation functions."""

    @pytest.mark.integration
    def test_count(self, driver, clean_db):
        """Test COUNT aggregation."""
        with driver.session() as session:
            session.run(
                """
                CREATE (:TestNode {type: 'A'})
                CREATE (:TestNode {type: 'A'})
                CREATE (:TestNode {type: 'B'})
                """
            )

            result = session.run(
                """
                MATCH (n:TestNode)
                RETURN n.type AS type, COUNT(n) AS count
                ORDER BY type
                """
            )
            records = list(result)
            assert records[0]["type"] == "A"
            assert records[0]["count"] == 2
            assert records[1]["type"] == "B"
            assert records[1]["count"] == 1

    @pytest.mark.integration
    def test_collect(self, driver, clean_db):
        """Test COLLECT aggregation."""
        with driver.session() as session:
            session.run(
                """
                CREATE (:TestNode {name: 'Alice', group: 'Team1'})
                CREATE (:TestNode {name: 'Bob', group: 'Team1'})
                CREATE (:TestNode {name: 'Charlie', group: 'Team2'})
                """
            )

            result = session.run(
                """
                MATCH (n:TestNode)
                RETURN n.group AS team, COLLECT(n.name) AS members
                ORDER BY team
                """
            )
            records = list(result)
            assert set(records[0]["members"]) == {"Alice", "Bob"}
            assert records[1]["members"] == ["Charlie"]

    @pytest.mark.integration
    def test_avg_sum(self, driver, clean_db):
        """Test AVG and SUM aggregations."""
        with driver.session() as session:
            session.run(
                """
                CREATE (:TestNode {value: 10})
                CREATE (:TestNode {value: 20})
                CREATE (:TestNode {value: 30})
                """
            )

            result = session.run(
                """
                MATCH (n:TestNode)
                RETURN AVG(n.value) AS avg, SUM(n.value) AS sum
                """
            )
            record = result.single()
            assert record["avg"] == 20.0
            assert record["sum"] == 60


class TestPathQueries:
    """Test path and traversal queries."""

    @pytest.mark.integration
    def test_variable_length_path(self, driver, clean_db):
        """Test variable-length path matching."""
        with driver.session() as session:
            # Create a chain: A -> B -> C -> D
            session.run(
                """
                CREATE (a:TestPerson {name: 'A'})
                CREATE (b:TestPerson {name: 'B'})
                CREATE (c:TestPerson {name: 'C'})
                CREATE (d:TestPerson {name: 'D'})
                CREATE (a)-[:KNOWS]->(b)-[:KNOWS]->(c)-[:KNOWS]->(d)
                """
            )

            # Find people 2 hops away from A
            result = session.run(
                """
                MATCH (a:TestPerson {name: 'A'})-[:KNOWS*2]->(target:TestPerson)
                RETURN target.name
                """
            )
            assert result.single()["target.name"] == "C"

            # Find people 1-3 hops away
            result = session.run(
                """
                MATCH (a:TestPerson {name: 'A'})-[:KNOWS*1..3]->(target:TestPerson)
                RETURN COLLECT(target.name) AS targets
                """
            )
            targets = result.single()["targets"]
            assert set(targets) == {"B", "C", "D"}

    @pytest.mark.integration
    def test_shortest_path(self, driver, clean_db):
        """Test shortest path finding."""
        with driver.session() as session:
            # Create two paths: A -> B -> D and A -> C -> D
            session.run(
                """
                CREATE (a:TestPerson {name: 'A'})
                CREATE (b:TestPerson {name: 'B'})
                CREATE (c:TestPerson {name: 'C'})
                CREATE (d:TestPerson {name: 'D'})
                CREATE (a)-[:KNOWS]->(b)-[:KNOWS]->(d)
                CREATE (a)-[:KNOWS]->(c)-[:KNOWS]->(d)
                """
            )

            result = session.run(
                """
                MATCH path = shortestPath(
                    (a:TestPerson {name: 'A'})-[:KNOWS*]-(d:TestPerson {name: 'D'})
                )
                RETURN length(path) AS hops
                """
            )
            assert result.single()["hops"] == 2


class TestParameters:
    """Test parameterized queries."""

    @pytest.mark.integration
    def test_parameterized_match(self, driver, clean_db):
        """Test using parameters in MATCH."""
        with driver.session() as session:
            session.run("CREATE (:TestNode {name: 'Target', value: 100})")

            # Query with parameters
            result = session.run(
                "MATCH (n:TestNode {name: $name}) RETURN n.value",
                name="Target"
            )
            assert result.single()["n.value"] == 100

    @pytest.mark.integration
    def test_parameterized_create(self, driver, clean_db):
        """Test using parameters in CREATE."""
        with driver.session() as session:
            session.run(
                "CREATE (n:TestNode {name: $name, value: $value})",
                name="ParamNode",
                value=42
            )

            result = session.run(
                "MATCH (n:TestNode {name: 'ParamNode'}) RETURN n.value"
            )
            assert result.single()["n.value"] == 42


# Unit tests that don't require Neo4j

class TestCypherPatterns:
    """Unit tests for Cypher pattern understanding (no Neo4j required)."""

    def test_pattern_syntax_understanding(self):
        """Test that we understand pattern syntax."""
        # These are just documentation tests
        node_pattern = "(variable:Label {property: value})"
        rel_pattern = "-[variable:TYPE {property: value}]->"
        path_pattern = "(a)-[:REL*1..3]->(b)"

        assert "Label" in node_pattern
        assert "TYPE" in rel_pattern
        assert "*1..3" in path_pattern

    def test_cypher_keywords(self):
        """Verify understanding of key Cypher keywords."""
        keywords = {
            "MATCH": "Find patterns in the graph",
            "CREATE": "Create new nodes/relationships",
            "MERGE": "Create if not exists",
            "SET": "Update properties",
            "DELETE": "Remove nodes/relationships",
            "RETURN": "Return results",
            "WHERE": "Filter conditions",
            "WITH": "Chain query parts",
        }

        assert len(keywords) == 8
        assert "MERGE" in keywords
