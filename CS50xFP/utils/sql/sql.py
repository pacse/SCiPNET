'''
SQL stuff
'''
from cs50 import SQL
from typing import cast
from pathlib import Path
from pydantic import BaseModel, field_validator, Field

# custom exception ╰(*°▽°*)╯
from .exceptions import *

# auto timestamping
from ..basic import timestamp # NOTE: `..` to go up a folder, add a `.` for another folder up


# Valid table names for SQL queries
VALID_TABLES = [
    "users",
    "scps",
    "mtfs",
    "sites",
    "audit_log",
    "clearance_levels",
    "containment_classes",
    "secondary_classes",
    "disruption_classes",
    "risk_classes",
    "titles",
    "colours"
]

# checks `table` against valid_tables
def validate_table(table: str) -> bool:
    '''
    Validate the table name against the list of valid tables.

    Returns True if the table is valid, False otherwise.
    '''
    return table in VALID_TABLES

# Deepwell database connection
DB_PATH = (Path(__file__).parent.parent.parent / "deepwell" / "SCiPnet.db").resolve()

try:
    db = SQL(f"sqlite:///{DB_PATH}")

except RuntimeError:
    raise DatabaseNotFoundError()


def next_id(table_name: str) -> int:
    '''
    Returns the next id in a table:
    COALESCE(MAX(id)) + 1
    '''

    # validate input
    if not validate_table(table_name):
        raise TableNotFoundError(table_name)

    # use COALESCE to prevent NULL for empty tables
    query = f"SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM {table_name}"

    try:
        return db.execute(query)[0]["next_id"]

    except Exception as e:
        raise DatabaseError(
            f"Failed to retrieve next ID from {table_name!r}:\n{e}\nQuery used: {query!r}"
        )


def get_field_with_field(table_name: str,
                         lookup_field: str, lookup_value: str | int,
                         return_field: str
                        ): # impossible to know return type
    '''
    Gets `return_field` from `table_name` where `lookup_field` = `lookup_value`
    '''
    # validate inputs
    if not validate_table(table_name):
        raise TableNotFoundError(table_name)

    if lookup_field == "id" and not isinstance(lookup_value, int):
        raise ValueError(f"Invalid ID: {lookup_value!r} (expected int, got {type(lookup_value).__name__})")

    elif lookup_field == "name" and not isinstance(lookup_value, str):
        raise ValueError(f"Invalid name: {lookup_value!r} (expected str, got {type(lookup_value).__name__})")

    elif lookup_field not in ["id", "name"]:
        raise ValueError(f"Invalid lookup field: {lookup_field!r} (expected 'id' or 'name')")

    try:
        query = f"SELECT {return_field} FROM {table_name} WHERE {lookup_field} = ?"
        return db.execute(query, lookup_value)[0][return_field]

    except IndexError:
        raise RecordNotFoundError(table_name, lookup_field, lookup_value)

    except (RuntimeError, KeyError): # db.execute will raise RuntimeError, KeyError just in case
        raise ColumnNotFoundError(lookup_field, table_name)

    except Exception as e:
        raise DatabaseError(
            f"Failed to retrieve {return_field!r} from {table_name!r} where {lookup_field} = {lookup_value}:\n{e}"
        )


def get_name(table: str, table_id: int) -> str:
    '''
    Gets the name of a row in a table by its ID

    returns the name as a string
    '''
    return get_field_with_field(table, "id", table_id, "name")


def get_nickname(MTF_id: int) -> str:
    '''
    Gets an MTF's nickname

    Returns the nickname as a string
    '''
    return get_field_with_field("mtfs", "id", MTF_id, "nickname")


def get_id(table: str, name: str) -> int:
    '''
    Gets the ID of a row in a table by its name

    Returns the ID as an integer
    '''
    return get_field_with_field(table, "name", name, "id")


def get_colour(id: int) -> int:
    '''
    Gets a ID's colour (for art.py) from a table

    Returns DB hex code
    '''
    return get_field_with_field("colours", "id", id, "hex_code")

def get_cc_colour(id: int) -> int:
    '''
    Gets a containment class's colour (for art.py)

    Returns a hex colour code
    '''
    # slightly different for containment classes,
    # prolly easier to hardcode (it's definately not a good idea to hardcode)
    if id == 1:
        colours = (0,159,107) # Green
    elif id == 2:
        colours = (255,211,0) # Yellow
    elif id == 3:
        colours = (192,2,51) # Red
    elif id == 4:
        colours = (66,66,72) # Grey
    elif id in range(5,9):
        colours = (252,252,252) # White (for explained, pending, esoteric, etc.)
    else:
        raise ValueError(f"Invalid containment class ID: {id}")

    # convert to hex & return
    return int("".join(f"{n:02x}" for n in colours), 16)


# Log events in the audit log (eg. account creation, login, file access, file edit, ect.)
def log_event(user_id: int,
              action: str,
              details: str,
              user_ip: str,
              timestamp: str = timestamp(),
              status: bool = True
            ) -> None:
    '''
    Logs an event in the audit log
    '''
    # validate inputs
    if not isinstance(user_id, int):
        raise ValueError(f"Invalid user_id: {user_id!r} (expected int, got {type(user_id).__name__})")

    if not isinstance(action, str):
        raise ValueError(f"Invalid action: {action!r} (expected str, got {type(action).__name__})")

    if not isinstance(details, str):
        raise ValueError(f"Invalid details: {details!r} (expected str, got {type(details).__name__})")

    if not isinstance(timestamp, str):
        raise ValueError(f"Invalid timestamp: {timestamp!r} (expected str, got {type(timestamp).__name__})")

    # execute query
    query = """
            INSERT INTO audit_log (user_id, action, details, user_ip, timestamp, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """
    return db.execute(query, user_id, action, details, user_ip, timestamp, status)
