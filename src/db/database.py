"""
Database configuration and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os
import logging

logger = logging.getLogger(__name__)

# Database URL - defaults to SQLite
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///trading_bot.db')

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={'check_same_thread': False} if 'sqlite' in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Session = scoped_session(SessionLocal)

# Base class for models
Base = declarative_base()


def init_db():
    """Initialize database tables"""
    from . import models  # Import models to register them
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")


def get_session():
    """Get a database session"""
    return Session()


def close_session():
    """Close the database session"""
    Session.remove()
