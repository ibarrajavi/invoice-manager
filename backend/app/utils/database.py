from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# Get DB URL from environment
DATABASE_URL = settings.DATABASE_URL

IS_SQLITE = DATABASE_URL.startswith("sqlite")

# Create the engine with SQLite flag
engine = create_engine(
    DATABASE_URL,
    # Setting "check_same_thread" to False allows multithreading for FastAPI
    # without raising an error
    connect_args={"check_same_thread": False} if IS_SQLITE else {},
)


if IS_SQLITE:

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, _):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")


# Session factory and Base for models
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
Base = declarative_base()


# Initialize DB
def init_db():
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)


# FastAPI dependency to provide a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
