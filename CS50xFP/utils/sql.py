'''
SQL stuff
'''
from cs50 import SQL
from dataclasses import dataclass
from typing import cast

# Deepwell database connection
db = SQL("sqlite:///deepwell/SCiPNET.db")

def next_id(table: str) -> int:
    '''
    Get the next id in a table:
    MAX(id) + 1
    '''
    return db.execute("SELECT MAX(id) + 1 as next_id FROM ?", 
                      table)[0]["next_id"]


def get_name(table: str, id: int | None) -> str:
    if id is None:
        return "None"
    else:
        return db.execute("SELECT name FROM ? WHERE id = ?", 
                        table, id)[0]["name"]

def get_nickname(id: int) -> str:
    '''
    Gets an MTF's nickname
    '''
    return db.execute("SELECT nickname FROM mtfs WHERE id = ?", 
                      id)[0]["nickname"]

def get_id(table: str, name: str) -> int:
    return db.execute("SELECT id FROM ? WHERE name = ?", 
                      table, name)[0]["id"]


def get_colour(id: int) -> int:
    '''
    Gets a ID's colour (for art.py) from a table
    '''
    # get colour & return
    return db.execute("SELECT hex_code FROM colours WHERE id = ?",
                             id)[0]["hex_code"]

def get_cc_colour(id: int) -> int:
    '''
    Gets a containment class's colour (for art.py)
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
def log_event(user_id: int, action: str, details: str = "") -> None:
    db.execute("INSERT INTO audit_log (user_id, action, details) VALUES (?, ?, ?)", user_id, action, details)

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
    title_id: int
    site_id: int
    override_phrase: str | None = None # not required for lower level personnel

def init_usr(info: dict[str, str | int | None]) -> User:
    '''
    Creates a user dataclass from
    the user's deepwell info
    '''

    return User(
        cast(int, info["id"]),
        cast(str, info["name"]),
        cast(str, info["password"]),
        cast(int, info["clearance_level_id"]),
        cast(int, info["title_id"]),
        cast(int, info["site_id"]),
        cast(str | None, info["override_phrase"])
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
                                cast((int | None), info["secondary_class_id"]))

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
    director: str | None = f"{info["director_id"]} - {info["director_name"]}" if info["director_id"] is not None else "[REDACTED]"

    return Site(
        id = cast(int,info["site_id"]),
        name = cast(str, info["site_name"]),
        director = director
    )