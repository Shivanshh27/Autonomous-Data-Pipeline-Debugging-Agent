import sqlite3
from pathlib import Path
from datetime import datetime, timezone


def initialize_database(db_path="data/processed/failure_history.db"):
    database_path = Path(db_path)

    database_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with sqlite3.connect(database_path) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                executed_at TEXT NOT NULL,
                status TEXT NOT NULL,
                total_failed_checks INTEGER NOT NULL,
                dataset_path TEXT NOT NULL
            )
        """)

    return str(database_path)


def save_pipeline_run(
    status,
    total_failed_checks,
    dataset_path,
    db_path="data/processed/failure_history.db"
):
    initialize_database(db_path)

    executed_at = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO pipeline_runs (
                executed_at,
                status,
                total_failed_checks,
                dataset_path
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                executed_at,
                status,
                total_failed_checks,
                dataset_path
            )
        )

        run_id = cursor.lastrowid

    return run_id


def get_pipeline_history(
    db_path="data/processed/failure_history.db"
):
    initialize_database(db_path)

    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute(
            """
            SELECT
                run_id,
                executed_at,
                status,
                total_failed_checks,
                dataset_path
            FROM pipeline_runs
            ORDER BY run_id DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]