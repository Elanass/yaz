from collections.abc import Generator

from sqlalchemy.orm import Session

from apps.surge.core.database import SessionLocal


def get_async_session() -> Generator[Session, None, None]:
    """Compatibility dependency that yields a sync SQLAlchemy Session.
    Note: The current database engine is synchronous.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
