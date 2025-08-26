'''
Database configuration settings
Controls db conn params and pooling settings
'''

from pathlib import Path

DB_PATH = (Path(__file__).parent.parent.parent / "deepwell" / "SCiPnet.db").resolve()
'''Path to the SQLite database'''

DB_URL = f"sqlite:///{DB_PATH}"
'''URL to connect to the database'''

POOL_CONFIG = {
    'pool_size': 5,         # amount of permanent db conns
    'max_overflow': 10,     # max num of temp db conns
    'pool_timeout': 30,     # seconds to wait for an available connection
    'pool_recycle': 3600    # recycle connections older than 1 hour
}
'''Connection pool configuration'''

SQLITE_CONFIG = {
    'isolation_level': 'SERIALIZABLE',  # enable strongest transaction isolation level
    'echo': True,                       # log sql queries to terminal
    'connect_args': {
        'timeout': 15,                  # connection timeout (15 seconds)
        'check_same_thread': False      # allow conns to be shared across threads (allow multithreading)
    }
}