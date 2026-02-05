"""Database session management"""
from src.infrastructure.database.config import SessionLocal


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
