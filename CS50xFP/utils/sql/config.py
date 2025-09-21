"""
Database configuration settings
Controls db conn params and pooling settings

Connection settings were made by Github Copilot
"""

from pathlib import Path

DB_PATH = (Path(__file__).parent.parent.parent / "deepwell" / "SCiPnet.db").resolve()
"""Path to the SQLite database"""

DB_URL = f"sqlite:///{DB_PATH}"
"""URL to connect to the database"""

POOL_CONFIG = {
    'pool_size': 10,       # amount of permanent db conns
    'max_overflow': 15,    # max num of additional db conns
    'pool_timeout': 30,    # seconds to wait for an available connection before throwing an error
    'pool_recycle': 500    # recycle older connections
}
"""Connection pool configuration"""

SQLITE_CONFIG = {
    'isolation_level': 'READ COMMITTED',  # only see commited data, allows for higher throughput than SERIALIZABLE while still being safe
    'echo': True,                         # log sql queries to terminal
    'connect_args': {
        'timeout': 30,                    # seconds to wait for transaction completion
        'check_same_thread': False        # allow conns to be shared across threads (allow multithreading)
    }
}
"""SQLite specific configuration"""
