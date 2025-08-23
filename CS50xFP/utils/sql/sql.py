'''
SQL stuff
'''
from cs50 import SQL
from dataclasses import dataclass
from typing import cast
from pathlib import Path
from pydantic import BaseModel

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


def validate_table(table: str) -> bool:
    '''
    Validate the table name against the list of valid tables.

    Returns True if the table is valid, False otherwise.
    '''
    return table in VALID_TABLES


# Deepwell database connection
DB_PATH = (Path(__file__).parent.parent.parent / "deepwell" / "SCiPnet.db").resolve()

db = SQL(f"sqlite:///{DB_PATH}")


def next_id(table_name: str) -> int:
    '''
    Returns the next id in a table:
    COALESCE(MAX(id)) + 1
    '''

    # validate input
    if not validate_table(table_name):
        raise TableNotFoundError(table_name)

    try:
        query = f"SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM {table_name}" # use COALESCE to prevent NULL for empty tables
        return db.execute(query)[0]["next_id"]

    except Exception as e:
        raise DatabaseError(
            f"Failed to retrieve next ID from {table_name!r}:\n{e}"
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
def log_event(user_id: int, action: str, details: str, user_ip: str, timestamp: str = timestamp(), status: bool = True) -> None:
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

''' 
Dataclasses for ease of
access for deepwell stuff 
'''
@dataclass(slots=True) # slots make it faster according to youtube ;)
class User:
    '''
    A dataclass to store user information after
    getting a user's data from the deepwell
    '''
    id: int
    name: str
    password: str
    clearance_level_id: int
    clearance_level_name: str
    title_id: int
    title_name: str
    site_id: int
    override_phrase: str | None = None # not required for lower level personnel

def init_usr(info: dict[str, str | int | None]) -> User:
    '''
    Creates a user dataclass from
    the user's deepwell info
    '''

    return User(
        id = cast(int, info["id"]),
        name = cast(str, info["name"]),
        password = cast(str, info["password"]),
        clearance_level_id = cast(int, info["clearance_level_id"]),
        clearance_level_name = get_name("clearance_levels", cast(int, info["clearance_level_id"])),
        title_id = cast(int, info["title_id"]),
        title_name = get_name("titles", cast(int, info["title_id"])),
        site_id = cast(int, info["site_id"]),
        override_phrase = cast(str | None, info["override_phrase"])
      )


@dataclass(slots=True)
class SCP_Colours:
    class_lvl: int
    cont_clss: int
    disrupt_clss: int
    rsk_clss: int

def init_colours(classification_level: int, containment_class: int,
                disruption_class: int, risk_class: int) -> SCP_Colours:
        '''
        Creates a SCP_COLOURS dataclass from
        deepwell values
        '''
        return SCP_Colours(
            class_lvl = get_colour(classification_level),
            cont_clss = get_cc_colour(containment_class),
            disrupt_clss = get_colour(disruption_class),
            rsk_clss = get_colour(risk_class)
        )

@dataclass(slots=True)
class SCP:
    '''
    A dataclass to store scp information after
    getting a scp's data from the deepwell
    '''
    id: int
    classification_level: str
    containment_class: str
    secondary_class: str | None
    disruption_class: str
    risk_class: str
    site_responsible_id: int | None
    assigned_task_force_name: str | None
    colours: SCP_Colours

def init_scp(info: dict[str, str | int | None]) -> SCP:
    # TODO!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # handle null values properly you lazy cabrone (╯°□°）╯︵ ┻━┻
    '''
    Creates a scp dataclass from
    the scp's deepwell info
    '''

    # get proper names from deepwell
    classification_level = get_name("clearance_levels",
                                    cast(int, info["classification_level_id"]))
        
    containment_class = get_name("containment_classes",
                                 cast(int, info["containment_class_id"]))
    
    
    secondary_class = get_name("secondary_classes",
                                cast(int, info["secondary_class_id"]))

    disruption_class = get_name('disruption_classes', cast(int, info['disruption_class_id']))
    
    risk_class = get_name("risk_classes", cast(int, info["risk_class_id"]))

    if info["assigned_task_force_id"]:
        atf_name = get_name("mtfs", cast(int, info["assigned_task_force_id"]))
        atf_nickname = get_nickname(cast(int, info["assigned_task_force_id"]))
        assigned_task_force_name = f"{atf_name} (*{atf_nickname}*)"
    else:
        assigned_task_force_name = None

    
    return SCP(
        id=cast(int, info["id"]),
        classification_level = classification_level,
        containment_class = containment_class,
        secondary_class = secondary_class,
        disruption_class = disruption_class,
        risk_class = risk_class,
        site_responsible_id = cast((int | None), info["site_responsible_id"]),
        assigned_task_force_name = assigned_task_force_name,
        
        colours = init_colours(
            classification_level = cast(int, info["classification_level_id"]),
            containment_class = cast(int, info["containment_class_id"]),
            disruption_class = cast(int, info["disruption_class_id"]),
            risk_class = cast(int, info["risk_class_id"]),
        )
    )


@dataclass(slots=True)
class Site:
    id: int
    name: str
    director: str | None

def init_site(info: dict[str, str | int | None]) -> Site:
    # format director
    director: str | None = f"{info['director_id']} - {info['director_name']}" if info["director_id"] is not None else "[REDACTED]"

    return Site(
        id = cast(int,info["site_id"]),
        name = cast(str, info["site_name"]),
        director = director
    )


@dataclass(slots=True)
class MTF:
    id: int
    name: str
    nickname: str
    leader_id: int | None
    leader_name: str | None
    site_id: int | None
    active: bool

def init_mtf(info: dict[str, str | int | None]) -> MTF:
    return MTF(
        id = cast(int, info["mtf_id"]),
        name = cast(str, info["mtf_name"]),
        nickname = cast(str, info["mtf_nickname"]),
        leader_id = cast(int | None, info["leader_id"]),
        leader_name = cast(str | None, info["leader_name"]),
        site_id = cast(int | None, info["mtf_site_id"]),
        active = cast(bool, info["mtf_active"])
    )