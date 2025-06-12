from cs50 import SQL
from dataclasses import dataclass

@dataclass
class User: # class to store user information after login
    id: int
    name: str
    password: str
    clearance_level: int
    title: str
    site: int
    phrase: str | None = None # not required for lower level personnel

def init_usr(info: dict) -> User:
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