'''
Connection functions were made by Github Copilot
'''
from sqlalchemy import create_engine

from .config import POOL_CONFIG, SQLITE_CONFIG, DB_URL
from .exceptions import DatabaseConnectionError

def create_db_engine():
    '''
    Creates a new SQLAlchemy database engine with
    settings from config.py for pool & SQLite
    '''
    try:
        return create_engine(
            DB_URL,         # path to SQLite database
            **POOL_CONFIG,  # unpack pool config settings (How the conn pool handles itself)
            **SQLITE_CONFIG  # unpack SQLite config settings (How SQLite handles itself)
        )

    except Exception as e:
        raise DatabaseConnectionError(f"Failed to create database engine:\n{e}")
