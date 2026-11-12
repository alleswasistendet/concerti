import sqlite3

import pytest

from database import database
from database.models import Concert


@pytest.fixture
def test_database(tmp_path, monkeypatch):
    """Create an isolated DB for each test."""

    database_path = tmp_path / "concerti_test.db"

    # Initialize the temporary DB
    database.initialize_database(database_path)

    # USe the temprary DB for all test operations
    monkeypatch.setattr(
        database, "get_connection", lambda: sqlite3.connect(database_path)
    )

    return database_path


def test_add_get_concert(test_database):
    """Test inserting and retrieving a concert."""

    concert = Concert(
        date="2026-11-12",
        title="Test",
        institution="Teatro",
        price=35.0,
        typology="Concerto",
        subtypology="Sinfonico",
        program="Programma",
        comment="Commento",
    )

    concert_id = database.add_concert(concert)

    stored_id, stored_concert = database.get_concert(concert_id)

    assert stored_id == concert_id
    assert stored_concert == concert


def test_add_concert_rollback(test_database):
    """Test inserting a wrong item in the DB."""

    concert = Concert(
        date="2026-11-12",
        title=None,
    )

    with pytest.raises(sqlite3.IntegrityError):
        database.add_concert(concert)

    assert database.get_concerts() == []


def test_get_concerts(test_database):
    """Test retrieving all concerts."""

    concert_1 = Concert(date="2026-11-12", title="Test 1", institution="Teatro")

    concert_2 = Concert(
        date="2026-11-11",
        title="Test 2",
        price=10.0,
    )

    concert_id_1 = database.add_concert(concert_1)
    concert_id_2 = database.add_concert(concert_2)

    concerts = database.get_concerts()

    assert concerts == [
        (concert_id_1, concert_1),
        (concert_id_2, concert_2),
    ]


def test_update_concert(test_database):
    """Test updating an existing concert in the DB."""

    concert = Concert(
        date="2026-11-12",
        title="Test",
        price=35.0,
    )

    concert_id = database.add_concert(concert)

    updated_concert = Concert(
        date="2026-11-11",
        title="Test aggiornato",
        institution="Teatro",
    )

    update_result = database.update_concert(concert_id, updated_concert)

    assert update_result == True
    assert database.get_concert(concert_id) == (concert_id, updated_concert)


def test_delete_concert(test_database):
    """Test deleting an existing concert from the DB."""

    concert = Concert(
        date="2026-11-12",
        title="Test",
    )

    concert_id = database.add_concert(concert)

    delete_result = database.delete_concert(concert_id)

    assert delete_result == True
    assert database.get_concert(concert_id) is None


def test_update_delete_of_nonexisting_concerts(test_database):
    """TEst updating and deleting a non existing concert in the DB."""

    concert_id = 100

    assert database.get_concert(concert_id) is None
    assert (
        database.update_concert(
            concert_id,
            Concert(
                date="2026-11-12",
                title="Test",
            ),
        )
        is False
    )
    assert database.delete_concert(concert_id) is False
