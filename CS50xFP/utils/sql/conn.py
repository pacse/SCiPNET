"""
Connection functions were made by Github Copilot
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm import Session as SessionType
from contextlib import contextmanager
from typing import Generator

from .config import POOL_CONFIG, SQLITE_CONFIG, DB_URL
from .exceptions import DatabaseConnectionError, DatabaseError

def create_db_engine():
    """
    Creates a new SQLAlchemy database engine with
    settings from config.py for pool & SQLite
    """
    try:
        return create_engine(
            DB_URL,         # path to SQLite database
            **POOL_CONFIG,  # unpack pool config settings (How the conn pool handles itself)
            **SQLITE_CONFIG  # unpack SQLite config settings (How SQLite handles itself)
        )

    except Exception as e:
        raise DatabaseConnectionError(f"Failed to create database engine:\n{e}")

# create a global engine instance, crashes import if init fails
engine = create_db_engine()
# create a factory to generate new sessions
Session_Factory = sessionmaker(bind=engine)
# ensures each thread gets its own session
Session = scoped_session(Session_Factory)

# allows func to use `with` for easier management
@contextmanager
def db_session() -> Generator[SessionType, None, None]:
    """
    Handles creation, action, and cleanup of a db session

    Usage:

    ```python
    with db_session() as session:
        session.add(some_object)
        session.query(SomeModel)
    ```
    """


    try:
        session = Session()  # create a new session
        yield session        # give it to the caller
        session.commit()     # commit what they did

    except Exception:
        session.rollback()   # undo what causes an error
        raise                # raise original error

    finally:
        session.close()      # ensure we always close the session
