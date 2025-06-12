from cs50 import SQL
from dataclasses import dataclass

@dataclass(slots=True)
class User:
    '''
    A dataclass to store important information after
    getting a user's data from the deepwell database
    '''
    id: int
    name: str
    password: str
    clearance_level: int
    title: str
    site: int
    phrase: str | None = None # not required for lower level personnel

def init_usr(info: dict) -> User:
    '''
    Stores user data from a deepewell
    request in a user dataclass
    '''
    id = info["id"]
    name = info["name"]
    password = info["password"]
    clearance_level = info["clearance_level_id"]
    title = info["title_id"]
    site = info["site_id"]
    phrase = info["phrase"]

    return User(id, name, password, clearance_level, title, site, phrase)

# SQL database
db = SQL("sqlite:///SCiPNETdeepwell.db")

def clear() -> None:
    '''
    Clears the screen
    '''
  if name == "nt":
    system("cls")
  elif use_colab:
    output.clear() # type: ignore
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