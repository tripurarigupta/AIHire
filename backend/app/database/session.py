from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from collections.abc import Generator
from app.core.config import settings

if not settings.DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")

engine = create_engine(
    settings.DATABASE_URL,
    echo = False,
    # The API runs as serverless functions that scale to zero and reuse
    # connections far less predictably than a long-lived server. Managed
    # Postgres closes connections that sit idle, so check a pooled connection
    # is still alive before handing it to a request, and recycle connections
    # before the database gets the chance to drop them.
    pool_pre_ping=True,
    pool_recycle=300,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()