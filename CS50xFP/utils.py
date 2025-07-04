import json
from cs50 import SQL # type: ignore
from dataclasses import dataclass
from datetime import datetime as dt
from typing import Any, cast, TypeAlias
from os import name, system
from os import get_terminal_size as gts
from rich.console import Console
from rich.markdown import Markdown
from urllib.parse import unquote
import socket
from time import sleep

Unknown: TypeAlias = Any # temp type for incomplete type annotations

# Information for server connection
HOST = "127.0.0.1" # localhost
PORT = 65432
ADDR = (HOST, PORT) # combine into a tuple
RCVSIZE = 1024 # buffer size for message length

''' Validate terminal size '''
try:
    SIZE = gts().columns
except OSError:
    SIZE = 120 # type: ignore

if SIZE < 120:
    raise Exception(f"Requires terminal size of 120 columns (current size {SIZE})")

''' SQL stuff '''
# Deepwell database connection
db = SQL("sqlite:///deepwell/SCiPNET.db")

# Get the next id in a table
def get_next_id(table: str) -> int:
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
    db.execute("INSERT INTO audit_log (id, user_id, action, details) VALUES (?, ?, ?, ?)", get_next_id("audit_log"), user_id, action, details)


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
    phrase: str | None = None # not required for lower level personnel

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
        cast(str, info["phrase"]) if info["phrase"] is not None else None
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
    site_responsible_id: int
    assigned_task_force_name: str | None

def init_scp(info: dict[str, str | int | None]) -> SCP:
    '''
    Creates a scp dataclass from
    the scp's deepwell info
    '''
    # get proper names from deepwell
    classification_level = get_name("clearance_levels",
                                    cast(int, info["classification_level_id"]))
    
    containment_class = get_name("containment_class",
                                 cast(int, info["containment_class_id"]))
    
    if info["secondary_class_id"] != 0: # 0 is null
        secondary_class = get_name("secondary_class",
                                   cast(int, info["secondary_class_id"]))
    else:
        secondary_class = None

    d_cls_gn = get_name('disruption_class', cast(int, info['disruption_class_id']))
    disruption_class = f"Level {info['disruption_class_id']} - {d_cls_gn}"
    
    r_cls_gn = get_name("risk_class", cast(int, info["risk_class_id"]))
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
        cast(int, info["site_responsible_id"]),
        assigned_task_force_name
    )


def encode(data: Any) -> bytes:
    # TODO: Validate
    '''
    Encodes data into json and converty it to bytes
    so it can be sent over a socket connection
    '''
    return json.dumps(data).encode()

def decode(data: bytes) -> Any:
    # TODO: Validate
    '''
    Decodes data from bytes to json
    so it can be processed by the server
    '''
    return json.loads(data.decode())

def clear() -> None:
    '''
    Clear the screen
    '''
    # OS is windows
    if name == 'nt':
        system("cls")
    # OS is mac or linux (or any other I guess, it's an else statement...)
    else:
        system("clear")

def printc(string: str) -> None:
  '''
  prints a line {string} centered to the terminal size
  '''
  print(f"{string:^{SIZE}}")

def timestamp() -> str:
  '''
  gets the current timestamp
  format: Day/Month/Year - Hour/min/second
  '''
  return dt.now().strftime("%d/%m/%Y - %H:%M:%S")


def display_scp(response: dict[str, Unknown], console: Console) -> None:
    '''
    Displays a scp after requested by user
    '''

    scp_info = init_scp(response["scp_info"]) #TODO: Move server side
    descs: dict[str, str] = response["descs"]
    SCPs: dict[str, str] = response["SCPs"]
    addenda: dict[str, str] = response["addenda"]

    # print scp_info
    md = Markdown(f"""# ITEM #: {scp_info.id}
## Object Class: {scp_info.containment_class}
## Secondary Class: {scp_info.secondary_class}
## Disruption Class: {scp_info.disruption_class}
## Risk Class: {scp_info.risk_class}
## Site Responsible: {scp_info.site_responsible_id}
## Assigned Task Force: {scp_info.assigned_task_force_name}
""")
    console.print(md)
    print() # space between

    # print Special Containment Procedures
    md = Markdown(f"## Special Containment Procedures:\n\n{SCPs['main']}")
    console.print(md)

    # print description
    md = Markdown(f"## Description:\n\n{descs['main']}")
    console.print(md)

    # allow other file showing
    if addenda:
        a_names: list[str] = [key for key in addenda.keys()]
    else:
        a_names = []
    desc_names: list[str] = [key for key in descs.keys()]
    SCP_names: list[str] = [key for key in SCPs.keys()]

    while True: # always offer more addenda after file access

        # make type checking happy
        i = 0
        j = 0
        k = 0
        print("Display additional addenda?")
        # first, addenda
        for i, name in enumerate(a_names):
            print(f"{i}: {unquote(name)}") # name is fname, so quoted
        
        # then descs
        if len(desc_names) > 1: # ensure there are other descs
            for j, name in enumerate(desc_names, 1):
                # skip main
                if name == "main":
                    continue
                # continue indexing from i
                print(f"{j+i}: {unquote(name)}")

        # finally SCPs
        if len(SCP_names) > 1:
            for k, name in enumerate(SCP_names):
                if name == "main":
                    continue
                # continue indexing
                print(f"{k+j+i}: {unquote(name)}")

        print("C: close file")

        inp = input("> ")

        # process decesion
        try:
            if inp.upper() == "C":
                return
            else:
                # what are they accessing
                idx = int(inp)

                # addenda?
                if idx <= i:
                    # access file
                    name = a_names[idx]
                    md = Markdown(f"## {unquote(name)}\n\n{addenda[name]}")
                    console.print(md)
                    # don't offer it again
                    a_names.pop(idx)
                
                # desc?
                elif idx <= j+i:
                    # access file
                    name = desc_names[idx-i-1]
                    md = Markdown(f"## {unquote(name)}\n\n{addenda[name]}")
                    console.print(md)
                    # don't offer it again
                    a_names.remove(name)

                # SCP?
                elif idx <= k+j+i:
                    # access file
                    name = SCP_names[idx-i-j-1]
                    md = Markdown(f"## {unquote(name)}\n\n{addenda[name]}")
                    console.print(md)
                    # don't offer it again
                    a_names.remove(name)

        except ValueError | IndexError:
            print(f"INVALID CHOICE: {inp!r}")

# Socket Send/Recv functions
def send(conn: socket.socket, data: Any) -> None:
    '''
    Sends data over conn with
    dynamic buffer size
    '''
    d = encode(data)
    buffer = len(d) * 8

    #TODO: Ensure buffer validity

    # now send data
    conn.sendall(encode(buffer))
    sleep(0.5)
    conn.sendall(d)

def recv(conn: socket.socket) -> bytes:
    '''
    Receives data from conn.
    Returns decoded data
    '''
    size = decode(conn.recv(RCVSIZE)) # size to recv
    assert isinstance(size, int) # verify size type
    return conn.recv(size) # return data

def c_create(server: socket.socket, type: str) -> None:
    '''
    Adds a {type} entry to the deepewell
    '''
    printc(f"CREATE {type.upper()}")

    send(server, f"CREATE {type.upper()}")
    response = recv(server)
    if not response: # sanity check
        printc("[ERROR]: NO RESPONSE FROM SERVER")
        return
    response = decode(response)

    assert isinstance(response, dict)

    # ensure we were valid
    if response == "INVALID":
        printc("Error")

    # seperate based on type
    if type == "SCP":
        scp = {}
        scp["id"] = input(f"ID (next: {response['id']}): ")
                    
        printc("Clearance Levels:")
        for c_level in response["clearance_levels"]:
            print(f"{c_level['name']}")

        scp["classification_level_id"] = int(input("Clearance Level: "))

        printc("Containment Classes:")
        for c_class in response["containment_classes"]:
            print(f"{c_class['id']} - {c_class['name']}")

        scp["containment_class_id"] = int(input("Containment Class: "))

        printc("Disruption Classes:")
        for d_class in response["disruption_classes"]:
            print(f"{d_class['id']} - {d_class['name']}")

        scp["disruption_class_id"] = int(input("Disruption Class: "))

        printc("Risk Classes:")
        for r_class in response["risk_classes"]:
            print(f"{r_class['id']} - {r_class['name']}")

        scp["risk_class_id"] = int(input("Risk Class: "))

        scp["site_responsible_id"] = int(input("Site Responsible: "))

        scp["assigned_task_force_id"] = input("Assigned Task Force (id): ")

        scp["special_containment_procedures"] = input("Special Containment Procedures: ")

        scp["description"] = input("Description: ")

        send(server, scp) # send scp data
        response = recv(server)
    
    elif type == "MTF":
        # TODO
        print("NOT YET IMPLEMENTED")

    elif type == "SITE":
        # TODO
        print("NOT YET IMPLEMENTED")

    elif type == "USER":
        # TODO
        print("NOT YET IMPLEMENTED")

    elif type == "SITE":
        # collect info
        name = input("Site Name (eg. Humanoid Containment Site-06-3)\n>>> ")
        print()
        director = input("Site Director (name or ID)\n>>> ")
        print()
        loc = input("Location (eg. Lorraine, Grand Est, France | 32, 40)\n>>> ")
        print()
        desc = input("Site Description\n>>> ")

        # send
        send(server, {
            "name":name,
            "director":director,
            "loc":loc,
            "desc":desc
        })

        result = recv(server)