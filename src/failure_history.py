from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from src.database import DATABASE_URL, engine
from src.models import Base, PipelineRun


def _get_engine(db_path=None) -> Engine:
    """
    Return the PostgreSQL engine for normal application usage.
    Use a separate SQLite database when a custom db_path is provided,
    primarily for isolated tests.
    """
    if db_path is None:
        return engine

    database_path = Path(db_path)
    database_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    database_url = f"sqlite:///{database_path.resolve().as_posix()}"

    return create_engine(
        database_url,
        connect_args={"check_same_thread": False},
    )


def initialize_database(db_path=None):
    """
    Initialize the pipeline history table.

    Normal application usage targets PostgreSQL.
    A custom db_path targets an isolated SQLite database.
    """
    database_engine = _get_engine(db_path)

    try:
        Base.metadata.create_all(
            bind=database_engine,
            tables=[PipelineRun.__table__],
            checkfirst=True,
        )
    finally:
        if db_path is not None:
            database_engine.dispose()

    if db_path is not None:
        return str(Path(db_path))

    return DATABASE_URL


def save_pipeline_run(
    status,
    total_failed_checks,
    dataset_path,
    db_path=None,
):
    initialize_database(db_path)

    database_engine = _get_engine(db_path)

    try:
        with Session(database_engine) as session:
            pipeline_run = PipelineRun(
                executed_at=datetime.now(timezone.utc),
                status=status,
                total_failed_checks=total_failed_checks,
                dataset_path=str(dataset_path),
            )

            session.add(pipeline_run)
            session.commit()
            session.refresh(pipeline_run)

            return pipeline_run.run_id

    finally:
        if db_path is not None:
            database_engine.dispose()


def get_pipeline_history(db_path=None):
    initialize_database(db_path)

    database_engine = _get_engine(db_path)

    try:
        with Session(database_engine) as session:
            statement = (
                select(PipelineRun)
                .order_by(PipelineRun.run_id.desc())
            )

            runs = session.scalars(statement).all()

            return [
                {
                    "run_id": run.run_id,
                    "executed_at": (
                        run.executed_at.isoformat()
                        if run.executed_at
                        else None
                    ),
                    "status": run.status,
                    "total_failed_checks": run.total_failed_checks,
                    "dataset_path": run.dataset_path,
                }
                for run in runs
            ]

    finally:
        if db_path is not None:
            database_engine.dispose()