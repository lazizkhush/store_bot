from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database.models import Base
import os

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///store_bot.db')

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging during development
    pool_pre_ping=True,
    connect_args={'check_same_thread': False} if 'sqlite' in DATABASE_URL else {}
)

# Create session factory
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(engine)
    print("✅ Database initialized successfully!")


def get_session():
    """Get database session"""
    return Session()


def close_session():
    """Close database session"""
    Session.remove()