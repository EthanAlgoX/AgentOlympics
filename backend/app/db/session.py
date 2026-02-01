from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Using SQLite for development ease, easy to swap with DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./agent_arena.db")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
