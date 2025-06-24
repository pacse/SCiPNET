import json
from cs50 import SQL # type: ignore
from dataclasses import dataclass
from datetime import datetime as dt
from typing import Any
from os import name, system
from os import get_terminal_size as gts

# Information for server connection
HOST = "127.0.0.1" # localhost
PORT = 65432
ADDR = (HOST, PORT) # combine into a tuple

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
    row = db.execute("SELECT MAX(id) + 1 as next_id FROM ?", table)
    return row[0]["next_id"]


def get_name(table: str, id: int) -> str:
    row = db.execute("SELECT name FROM ? WHERE id = ?", table, id)
    return row[0]["name"]

def get_id(table: str, name: str) -> int:
    row = db.execute("SELECT id FROM ? WHERE name = ?", table, name)
    return row[0]["id"]


# Log events in the audit log (eg. account creation, login, file access, file edit, ect.)
def log_event(user_id: int, action: str, details: str = "") -> None:
    db.execute("INSERT INTO audit_log (id, user_id, action, details) VALUES (?, ?, ?, ?)", get_next_id("audit_log"), user_id, action, details)


''' Dataclass to store usr info '''

@dataclass(slots=True)
class User:
    '''
    A dataclass to store information after
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
    Stores user data from a deepwell
    request in a user dataclass
    '''

    return User(
        int(info["id"]), # type: ignore
        str(info["name"]), # type: ignore
        str(info["password"]), # type: ignore
        int(info["clearance_level_id"]), # type: ignore
        str(info["title_id"]), # type: ignore
        int(info["site_id"]), # type: ignore
        info["phrase"] if info["phrase"] is not None else None # type: ignore
      )

def encode(data: Any) -> Any:
    # TODO: Validate
    '''
    Encodes data into json and converty it to bytes
    so it can be sent over a socket connection
    '''
    return json.dumps(data).encode()


def decode(data: Any) -> Any:
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

# print(f"{'':^{SIZE}}")
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


def handle_reply(reply: str):
    '''
    Handles a server response client side
    '''
    pass

def handle_request(request: str):
    '''
    
    '''
