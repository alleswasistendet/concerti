import sqlite3
from pathlib import Path

from database.models import Concert

DATABASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = DATABASE_DIR / "concerti.db"
SCHEMA_PATH = DATABASE_DIR / "schema.sql"


###########################
#### Utility functions ####
###########################


def convert_to_concert(row: tuple) -> Concert:
    """Convert a DB row into a Concert object."""

    return Concert(
        date=row[1],
        institution=row[2],
        title=row[3],
        price=row[4],
        typology=row[5],
        subtypology=row[6],
        program=row[7],
        comment=row[8],
    )


###########################
#### Core DB functions ####
###########################


def get_connection(database_path: Path = DATABASE_PATH) -> sqlite3.Connection:
    """Open a connection to the concerts DB."""
    return sqlite3.connect(database_path)


def initialize_database(database_path: Path = DATABASE_PATH) -> None:
    """Create the database tables if they do not exist."""

    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    connection = get_connection(database_path)

    try:
        connection.executescript(schema)
        connection.commit()
    finally:
        connection.close()


def add_concert(concert: Concert) -> int:
    """Insert a concert into the database and return its ID."""

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO concerts (
                concert_date, institution, title, price,
                typology, subtypology, program, comment
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                concert.date,
                concert.institution,
                concert.title,
                concert.price,
                concert.typology,
                concert.subtypology,
                concert.program,
                concert.comment,
            ),
        )

        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()


def get_concerts() -> list[tuple[int, Concert]]:
    """Return all concerts from the DB."""

    connection = get_connection()

    try:
        cursor = connection.execute("SELECT * FROM concerts ORDER BY concert_date DESC")
        return [(row[0], convert_to_concert(row)) for row in cursor.fetchall()]

    finally:
        connection.close()


def get_concert(concert_id: int) -> tuple[int, Concert] | None:
    """Return a concert by ID, or None if it does not exist."""

    connection = get_connection()

    try:
        cursor = connection.execute(
            "SELECT * FROM concerts WHERE id = ?",
            (concert_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None
        return row[0], convert_to_concert(row)

    finally:
        connection.close()


def update_concert(
    concert_id: int,
    concert: Concert,
) -> bool:
    """Update a concert and return whether it existed."""

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE concerts
            SET
                concert_date = ?,
                institution = ?,
                title = ?,
                price = ?,
                typology = ?,
                subtypology = ?,
                program = ?,
                comment = ?
            WHERE id = ?
            """,
            (
                concert.date,
                concert.institution,
                concert.title,
                concert.price,
                concert.typology,
                concert.subtypology,
                concert.program,
                concert.comment,
                concert_id,
            ),
        )

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()


def delete_concert(concert_id: int) -> bool:
    """Delete a concert and return whether it existed."""

    connection = get_connection()

    try:
        cursor = connection.execute("DELETE FROM concerts WHERE id = ?", (concert_id,))

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()
