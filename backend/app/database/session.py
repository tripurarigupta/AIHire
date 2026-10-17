from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from collections.abc import Generator
from app.core.config import settings

if not settings.DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")

engine = create_engine(
    settings.DATABASE_URL,
    echo = False
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