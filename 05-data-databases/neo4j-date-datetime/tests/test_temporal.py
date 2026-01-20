"""
Tests for Neo4j temporal types.

These tests require Neo4j to be running.
Run with: make test-integration
"""

import os
import pytest
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable


def get_driver():
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    return GraphDatabase.driver(uri, auth=(user, password))


@pytest.fixture(scope="module")
def driver():
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
    def cleanup():
        with driver.session() as session:
            session.run("MATCH (n:TemporalTest) DETACH DELETE n")
    cleanup()
    yield
    cleanup()


class TestDateType:
    """Test DATE type operations."""

    @pytest.mark.integration
    def test_create_date_from_string(self, driver, clean_db):
        """Test creating DATE from ISO string."""
        with driver.session() as session:
            result = session.run("""
                CREATE (n:TemporalTest {d: date('2024-03-15')})
                RETURN n.d AS d
            """)
            record = result.single()
            assert str(record["d"]) == "2024-03-15"

    @pytest.mark.integration
    def test_create_date_from_components(self, driver, clean_db):
        """Test creating DATE from components."""
        with driver.session() as session:
            result = session.run("""
                CREATE (n:TemporalTest {d: date({year: 2024, month: 3, day: 15})})
                RETURN n.d AS d
            """)
            record = result.single()
            assert record["d"].year == 2024
            assert record["d"].month == 3
            assert record["d"].day == 15

    @pytest.mark.integration
    def test_date_comparison(self, driver, clean_db):
        """Test DATE comparison operators."""
        with driver.session() as session:
            session.run("""
                CREATE (:TemporalTest {name: 'A', d: date('2024-01-01')})
                CREATE (:TemporalTest {name: 'B', d: date('2024-06-15')})
                CREATE (:TemporalTest {name: 'C', d: date('2024-12-31')})
            """)

            result = session.run("""
                MATCH (n:TemporalTest)
                WHERE n.d > date('2024-06-01')
                RETURN n.name ORDER BY n.d
            """)
            names = [r["n.name"] for r in result]
            assert names == ["B", "C"]

    @pytest.mark.integration
    def test_date_components(self, driver, clean_db):
        """Test extracting DATE components."""
        with driver.session() as session:
            result = session.run("""
                WITH date('2024-03-15') AS d
                RETURN d.year, d.month, d.day, d.dayOfWeek, d.dayOfYear
            """)
            record = result.single()
            assert record["d.year"] == 2024
            assert record["d.month"] == 3
            assert record["d.day"] == 15
            assert record["d.dayOfWeek"] == 5  # Friday
            assert record["d.dayOfYear"] == 75


class TestDateTimeType:
    """Test DATETIME type operations."""

    @pytest.mark.integration
    def test_create_datetime_utc(self, driver, clean_db):
        """Test creating DATETIME with UTC timezone."""
        with driver.session() as session:
            result = session.run("""
                CREATE (n:TemporalTest {dt: datetime('2024-03-15T14:30:00Z')})
                RETURN n.dt AS dt
            """)
            record = result.single()
            assert record["dt"].hour == 14
            assert record["dt"].minute == 30

    @pytest.mark.integration
    def test_datetime_timezone_conversion(self, driver, clean_db):
        """Test converting DATETIME between timezones."""
        with driver.session() as session:
            result = session.run("""
                WITH datetime('2024-03-15T12:00:00Z') AS utc
                RETURN utc,
                       datetime({datetime: utc, timezone: 'America/New_York'}) AS nyc
            """)
            record = result.single()
            # NYC is UTC-4 or UTC-5 depending on DST
            assert record["nyc"].hour != record["utc"].hour

    @pytest.mark.integration
    def test_datetime_components(self, driver, clean_db):
        """Test extracting DATETIME components."""
        with driver.session() as session:
            result = session.run("""
                WITH datetime('2024-03-15T14:30:45.123Z') AS dt
                RETURN dt.hour, dt.minute, dt.second, dt.millisecond
            """)
            record = result.single()
            assert record["dt.hour"] == 14
            assert record["dt.minute"] == 30
            assert record["dt.second"] == 45
            assert record["dt.millisecond"] == 123


class TestDuration:
    """Test Duration operations."""

    @pytest.mark.integration
    def test_create_duration(self, driver, clean_db):
        """Test creating duration values."""
        with driver.session() as session:
            result = session.run("""
                RETURN duration({days: 30}) AS d,
                       duration({months: 1}) AS m,
                       duration({hours: 24}) AS h
            """)
            record = result.single()
            assert record["d"] is not None
            assert record["m"] is not None
            assert record["h"] is not None

    @pytest.mark.integration
    def test_add_duration_to_date(self, driver, clean_db):
        """Test adding duration to date."""
        with driver.session() as session:
            result = session.run("""
                WITH date('2024-01-15') AS d
                RETURN d + duration({days: 30}) AS result
            """)
            record = result.single()
            assert str(record["result"]) == "2024-02-14"

    @pytest.mark.integration
    def test_duration_between_dates(self, driver, clean_db):
        """Test calculating duration between dates."""
        with driver.session() as session:
            result = session.run("""
                WITH date('2024-01-01') AS start, date('2024-01-31') AS end
                RETURN duration.inDays(start, end).days AS days
            """)
            record = result.single()
            assert record["days"] == 30

    @pytest.mark.integration
    def test_subtract_duration(self, driver, clean_db):
        """Test subtracting duration from date."""
        with driver.session() as session:
            result = session.run("""
                WITH date('2024-03-15') AS d
                RETURN d - duration({days: 14}) AS result
            """)
            record = result.single()
            assert str(record["result"]) == "2024-03-01"


class TestTemporalPatterns:
    """Test common temporal query patterns."""

    @pytest.mark.integration
    def test_filter_by_date_range(self, driver, clean_db):
        """Test filtering by date range."""
        with driver.session() as session:
            session.run("""
                CREATE (:TemporalTest {name: 'Jan', d: date('2024-01-15')})
                CREATE (:TemporalTest {name: 'Mar', d: date('2024-03-15')})
                CREATE (:TemporalTest {name: 'Jun', d: date('2024-06-15')})
            """)

            result = session.run("""
                MATCH (n:TemporalTest)
                WHERE date('2024-02-01') <= n.d <= date('2024-05-31')
                RETURN n.name
            """)
            names = [r["n.name"] for r in result]
            assert names == ["Mar"]

    @pytest.mark.integration
    def test_group_by_month(self, driver, clean_db):
        """Test grouping by month."""
        with driver.session() as session:
            session.run("""
                CREATE (:TemporalTest {d: date('2024-01-10')})
                CREATE (:TemporalTest {d: date('2024-01-20')})
                CREATE (:TemporalTest {d: date('2024-02-15')})
            """)

            result = session.run("""
                MATCH (n:TemporalTest)
                RETURN n.d.month AS month, COUNT(n) AS count
                ORDER BY month
            """)
            records = list(result)
            assert records[0]["month"] == 1
            assert records[0]["count"] == 2
            assert records[1]["month"] == 2
            assert records[1]["count"] == 1


class TestTemporalUnderstanding:
    """Unit tests for temporal concepts (no Neo4j required)."""

    def test_iso_format_understanding(self):
        """Test understanding of ISO 8601 format."""
        # These are documentation tests
        date_format = "YYYY-MM-DD"
        datetime_format = "YYYY-MM-DDTHH:MM:SS"
        datetime_utc = "YYYY-MM-DDTHH:MM:SSZ"
        datetime_offset = "YYYY-MM-DDTHH:MM:SS+HH:MM"

        assert "T" in datetime_format  # T separates date and time
        assert "Z" in datetime_utc  # Z indicates UTC

    def test_temporal_type_selection(self):
        """Test understanding of when to use each type."""
        use_cases = {
            "birthday": "DATE",
            "meeting_start": "DATETIME",
            "local_schedule": "LOCALDATETIME",
            "audit_log": "DATETIME",
            "holiday": "DATE",
            "store_hours": "TIME",
        }

        assert use_cases["birthday"] == "DATE"
        assert use_cases["audit_log"] == "DATETIME"
