'''
Script to recreate the sql database
'''
import sqlite3
from cs50 import SQL
from sys import argv

# usage: python quickstart.py [DB Name]

# create database
if len(argv) > 1:
    # we have a db name
    name = argv[1]
    with sqlite3.connect(argv[1]):
        pass

else:    
    # use default
    name = "SCiPNET.db"
    with sqlite3.connect("SCiPNET.db"):
        pass

# open with SQL
db = SQL(f"sqlite:///{name}")

# === create tables ===

# users
db.execute("""CREATE TABLE users (
id INTEGER AUTOINCREMENT PRIMARY KEY NOT NULL,
name TEXT NOT NULL,
password TEXT NOT NULL, -- add later: store securely (hashing + salting)
clearance_level_id INTEGER NOT NULL,
title_id INTEGER NOT NULL,
site_id INTEGER NOT NULL,
phrase TEXT, -- Override phrase, optional field
last_login DATETIME DEFAULT NULL,

FOREIGN KEY(site_id) REFERENCES sites(id),
FOREIGN KEY(clearance_level_id) REFERENCES clearance_levels(id),
FOREIGN KEY(title_id) REFERENCES titles(id)
)""")

# mtfs
db.execute("""CREATE TABLE mtfs (
id INTEGER AUTOINCREMENT PRIMARY KEY NOT NULL,
name TEXT NOT NULL, -- eg. Epsilon-6
nickname TEXT NOT NULL, -- eg. "Village Idiots"
leader INTEGER, -- probably null when ripped from wikidot
active BOOLEAN DEFAULT TRUE,

FOREIGN KEY(leader) REFERENCES users(id)
)
""")

# scps
db.execute("""CREATE TABLE scps (
id INTEGER AUTOINCREMENT PRIMARY KEY NOT NULL,
classification_level_id INTEGER NOT NULL,
containment_class_id INTEGER NOT NULL,
secondary_class_id INTEGER,
disruption_class_id INTEGER,
risk_class_id INTEGER,
site_responsible_id INTEGER NOT NULL, -- should it be not null?
assigned_task_force_id INTEGER, -- safe one's prolly don't need a task force
archived BOOLEAN DEFAULT FALSE NOT NULL, -- weather or not the file's been archived (neutralized, explained, ect)

FOREIGN KEY(classification_level_id) REFERENCES clearance_levels(id),
FOREIGN KEY(containment_class_id) REFERENCES containment_classes(id),
FOREIGN KEY(secondary_class_id) REFERENCES secondary_classes(id),
FOREIGN KEY(disruption_class_id) REFERENCES disruption_classes(id),
FOREIGN KEY(risk_class_id) REFERENCES risk_classes(id),
FOREIGN KEY(site_responsible_id) REFERENCES sites(id),
FOREIGN KEY(assigned_task_force_id) REFERENCES mtfs(id)
)""")