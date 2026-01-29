"""
Database engine, session, and initialization logic
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_FILE

DATABASE_URL = f"sqlite:///{DATABASE_FILE}"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
