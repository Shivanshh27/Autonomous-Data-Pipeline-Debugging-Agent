from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


PROJECT_ROOT = Path.cwd()

DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "failure_history.db"

DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass