from rich.console import Console
from rich.markdown import Markdown
from urllib.parse import unquote
from cs50 import SQL
import os

# disable markdown_it logging
import logging
logging.getLogger("markdown_it").setLevel(logging.WARNING)

db = SQL("sqlite:///SCiPNET.db")

scp = 2
path = f"./scps/{scp}"

# get f_data
objclss = db.execute("""SELECT name from containment_classes WHERE id = (
                     SELECT containment_class_id FROM scps WHERE id = ?)""", scp)
if not objclss:
    raise ValueError(f"SCP-{scp:03d} does not exist in the database.")
objclss = objclss[0]

# file time!
SCPs = {}
SCP_names = os.listdir(f"{path}/SCPs")
for name in SCP_names:
    with open(f"{path}/SCPs/{name}", "r", encoding="utf-8") as f:
        SCPs[name] = f.read()

descs = {}
desc_names = os.listdir(f"{path}/descs")
for name in desc_names:
    with open(f"{path}/descs/{name}", "r", encoding="utf-8") as f:
        descs[name] = f.read()

addenda = {}
addenda_names = os.listdir(f"{path}/addenda")
for name in addenda_names:
    with open(f"{path}/addenda/{name}", "r", encoding="utf-8") as f:
        addenda[name] = f.read()


# display md in terminal
console = Console()

# print headings
console.print(Markdown(f"# **Item #:** SCP-{scp:03d}"))
console.print(Markdown(f"## **Object Class:** {objclss}"))

print() # separator

# print SCPs
console.print(Markdown(f"## **Special Containment Procedures:**\n{SCPs['main.md']}"))

# print description
console.print(Markdown(f"## **Description:**\n{descs['main.md']}"))

# print addenda
if addenda:
    for name in addenda_names:
        console.print(Markdown(f"## **{unquote(name).replace('.md', '')}:**\n{addenda[name]}"))