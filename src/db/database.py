from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


def create_session_factory(database_url: str) -> sessionmaker[Session]:
    engine = create_engine(database_url, pool_pre_ping=True)
    return sessionmaker(bind=engine, expire_on_commit=False)


def create_schema(database_url: str) -> None:
    from . import models

    engine = create_engine(database_url, pool_pre_ping=True)
    Base.metadata.create_all(engine)


def get_session(database_url: str) -> Generator[Session, None, None]:
    factory = create_session_factory(database_url)
    with factory() as session:
        yield session
