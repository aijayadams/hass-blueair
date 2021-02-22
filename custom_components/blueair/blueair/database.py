"""This module contains a class that can be used to store and retrieve measurements to/from a SQLite database."""

import sqlite3

from typing import Dict, Optional, Sequence, Union

class Database(object):
    """This class provides a wrapper around a SQLite database for storing/retrieving measurements."""

    def __init__(self, filename: str = "blueair.db") -> None:
        """Instantiate a new database using the provided filename."""
        self.db = sqlite3.connect(filename)
        self.db.row_factory = sqlite3.Row  # type: ignore
        self.cursor = self.db.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY ASC,
                timestamp INTEGER NOT NULL UNIQUE,
                pm25 REAL NOT NULL,
                temperature REAL NOT NULL,
                humidity REAL NOT NULL,
                co2 REAL NOT NULL,
                voc REAL NOT NULL,
                all_pollution REAL NOT NULL
            );
        """)

        self.db.commit()

    def commit(self) -> None:
        """Commit changes to the database."""
        self.db.commit()

    def get_latest_timestamp(self) -> Optional[int]:
        """
        Retrieve the latest stored measurement timestamp from the database.

        Returns None if there is no such timestamp.
        """
        self.cursor.execute("""
            SELECT MAX(timestamp) FROM measurements;
        """)

        return self.cursor.fetchone()[0]  # type: ignore

    def get_all_measurements(self) -> Sequence[Dict[str, Union[str, int, float]]]:
        """Retrieve all stored measurements from the database."""
        self.cursor.execute("""
            SELECT * FROM measurements ORDER BY timestamp ASC;
        """)

        return (dict(row) for row in self.cursor.fetchall())  # type: ignore

    def insert_measurement(self, *, timestamp: int, pm25: float, temperature: float, humidity: float, co2: float, voc: float, all_pollution: float) -> None:
        """
        Insert a new measurement into the database.

        For performance reasons this does not actually commit the newly created
        record to disk. Call `commit` after inserting the last record of a
        batch to save them to disk.
        """
        self.cursor.execute("""
            INSERT INTO measurements (
                timestamp, pm25, temperature, humidity, co2, voc, all_pollution
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?
            );
        """, (timestamp, pm25, temperature, humidity, co2, voc, all_pollution))
