"""Database configuration and engine setup"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.configs.config import load_settings

# Load settings
settings = load_settings()

# Create database engine with pre-ping to handle long-running idle connections
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={"options": "-c statement_timeout=3600000"} # 1 hour timeout
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()
