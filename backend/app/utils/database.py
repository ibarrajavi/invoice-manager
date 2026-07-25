from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# Get DB URL from environment
DATABASE_URL = settings.DATABASE_URL

# Create the engine with SQLite flag
engine = create_engine(
    DATABASE_URL,
    # Setting "check_same_thread" to False allows multithreading for FastAPI
    # without raising an error
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Session factory and Base for models
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
Base = declarative_base()

# Initialize DB
def init_db():
    import app.models
    Base.metadata.create_all(bind=engine)

# FastAPI dependency to provide a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

