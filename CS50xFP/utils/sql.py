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

def get_name(table: str, id: int) -> str:
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
        cast(str, info["override_phrase"]) if info["override_phrase"] is not None else None
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

def init_scp(info: dict[str, str | int | None]) -> SCP:
    # TODO!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # handle null values properly you lazy cabrone (╯°□°）╯︵ ┻━┻
    '''
    Creates a scp dataclass from
    the scp's deepwell info
    '''
    def _formatname(table: str, id: int):
        gn = get_name(table, id)
        return f"Level {id} - {gn}"

    # get proper names from deepwell
    classification_level = _formatname("clearance_levels",
                                       cast(int, info["classification_level_id"]))
    
    containment_class = _formatname("containment_classes",
                                    cast(int, info["containment_class_id"]))
    
    
    if info["secondary_class_id"]:
        secondary_class = get_name("secondary_classes",
                                   cast(int, info["secondary_class_id"]))
    else:
        secondary_class = None

    d_cls_gn = get_name('disruption_classes', cast(int, info['disruption_class_id']))
    disruption_class = f"Level {info['disruption_class_id']} - {d_cls_gn}"
    
    r_cls_gn = get_name("risk_classes", cast(int, info["risk_class_id"]))
    risk_class = f"Level {info['risk_class_id']} - {r_cls_gn}"

    if info["assigned_task_force_id"]:
        atf_name = get_name("mtfs", cast(int, info["assigned_task_force_id"]))
        atf_nickname = get_nickname(cast(int, info["assigned_task_force_id"]))
        assigned_task_force_name = f"{atf_name} (*{atf_nickname}*)"
    else:
        assigned_task_force_name = None

    
    return SCP(
        cast(int, info["id"]),
        classification_level,
        containment_class,
        secondary_class,
        disruption_class,
        risk_class,
        cast((int | None), info["site_responsible_id"]),
        assigned_task_force_name
    )
