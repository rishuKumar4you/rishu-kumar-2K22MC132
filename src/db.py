# src/db.py
from sqlmodel import SQLModel, Session, create_engine
from contextlib import contextmanager

# SQLite database URL
DATABASE_URL = "sqlite:///./boostly.db"

# Create engine
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

def create_db_and_tables():
    """Create all database tables"""
    SQLModel.metadata.create_all(engine)

@contextmanager
def get_session():
    """Context manager for database sessions"""
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()

