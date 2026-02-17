"""Database configuration and engine setup"""
import uuid
from contextvars import ContextVar
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from src.configs.config import load_settings

# Load settings
settings = load_settings()

# ContextVar to store the session ID for the current request scope
session_id_var = ContextVar("session_id", default=None)

def get_session_id():
    return session_id_var.get()

# Create database engine with pre-ping to handle long-running idle connections
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=20,
    max_overflow=20,
    connect_args={"options": "-c statement_timeout=3600000"} # 1 hour timeout
)

# Create session factory
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Scoped session that uses the ContextVar to distinguish between requests
# This ensures that all components in a single request share the same session instance
SessionLocal = scoped_session(session_factory, scopefunc=get_session_id)

# Base class for ORM models
Base = declarative_base()
