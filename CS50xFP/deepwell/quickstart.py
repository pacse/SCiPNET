'''
Script to recreate the sql database
usage: python quickstart.py [DB Name (optional)]
'''
import sqlite3
from cs50 import SQL
from sys import argv


# what do we name db?
if len(argv) not in [1,2]:
    # improper usage
    raise ValueError(f"Impropper usage:\nExpected 1 or 2 cli's, recived {len(argv)}")

elif len(argv) == 2:
    # we have a db name
    name = argv[1]

else:
    # use default
    name = "SCiPNET.db"

# create database
with sqlite3.connect(name):
    pass

# open with cs50 SQL
db = SQL(f"sqlite:///{name}")


# === create and init helper tables ===

# clearance levels
db.execute("""CREATE TABLE clearance_levels (
id INTEGER PRIMARY KEY,
name TEXT NOT NULL, -- ie. Secret, Thaumiel, ect.
)""")

for c_lvl in [
              "Unrestricted",
              "Restricted",
              "Confidential",
              "Secret",
              "Top Secret",
              "Cosmic Top Secret"]:
    db.execute("INSERT INTO clearance_levels (name) VALUES (?)", c_lvl)

# containment classes
db.execute("""CREATE TABLE containment_classes (
id INTEGER PRIMARY KEY,
name TEXT NOT NULL, -- eg. Safe, Euclid, Keter, ect.
)""")

for c_clss in [
               "Safe",
               "Euclid",
               "Keter",
               "Neutralized",
               "Explained",
               "Decommissioned",
               "Uncontained",
                "Pending",]:
    db.execute("INSERT INTO containment_classes (name) VALUES (?)", c_clss)

# secondary classes
db.execute("""CREATE TABLE secondary_classes (
id INTEGER PRIMARY KEY,
name TEXT NOT NULL, -- eg. Thaumiel, Appolyion, ect.
)""")

# basic init while not used
db.execute("INSERT INTO secondary_classes (id, name) VALUES (0, 'None')")

# disruption classes
db.execute("""CREATE TABLE disruption_classes (
id INTEGER PRIMARY KEY,
name TEXT NOT NULL, -- eg. Dark, Vlam, ect.
)""")

for d_clss in [
               "Dark",
               "Vlam",
               "Keneq",
               "Ekhi",
               "Amida"]:
    db.execute("INSERT INTO disruption_classes (name) VALUES (?)", d_clss)

# risk classes
db.execute("""CREATE TABLE risk_classes (
id INTEGER PRIMARY KEY,
name TEXT NOT NULL, -- eg. Notice, Danger, ect.
)""")

for r_clss in [
               "Notice",
               "Caution",
               "Warning",
               "Danger",
               "Critical"]:
    db.execute("INSERT INTO risk_classes (name) VALUES (?)", r_clss)

# titles
db.execute("""CREATE TABLE titles (
id INTEGER PRIMARY KEY,
name TEXT NOT NULL, -- title (eg. site director, junior researcher, O5 council member)
)""")

for title in ["Containment Specialist",
              "Researcher",
              "Security Officer",
              "Tactical Response Officer",
              "Field Agent",
              "Mobile Task Force Operative",
              "Site Director",
              "O5 Council Member"]:
    db.execute("INSERT INTO titles (name) VALUES (?)", title)


# === create main tables ===

# users
db.execute("""CREATE TABLE users (
id INTEGER PRIMARY KEY,
name TEXT NOT NULL,
password TEXT NOT NULL, -- add later: store securely (hashing + salting)
clearance_level_id INTEGER NOT NULL,
title_id INTEGER NOT NULL,
site_id INTEGER NOT NULL,
override_phrase TEXT, -- Override phrase, optional field (phrase -> override_phrase for clarity)
last_login DATETIME DEFAULT NULL,

FOREIGN KEY(site_id) REFERENCES sites(id),
FOREIGN KEY(clearance_level_id) REFERENCES clearance_levels(id),
FOREIGN KEY(title_id) REFERENCES titles(id)
)""")

# scps
db.execute("""CREATE TABLE scps (
id INTEGER PRIMARY KEY NOT NULL,
classification_level_id INTEGER NOT NULL,
containment_class_id INTEGER NOT NULL,
secondary_class_id INTEGER,
disruption_class_id INTEGER,
risk_class_id INTEGER,
site_responsible_id INTEGER NOT NULL,
assigned_task_force_id INTEGER,
status TEXT DEFAULT "active" CHECK(status IN ("active", "neutralized", "explained", "deleted")) -- Thanks ChatGPT for improving this from a bool :)

FOREIGN KEY(classification_level_id) REFERENCES clearance_levels(id),
FOREIGN KEY(containment_class_id) REFERENCES containment_classes(id),
FOREIGN KEY(secondary_class_id) REFERENCES secondary_classes(id),
FOREIGN KEY(disruption_class_id) REFERENCES disruption_classes(id),
FOREIGN KEY(risk_class_id) REFERENCES risk_classes(id),
FOREIGN KEY(site_responsible_id) REFERENCES sites(id),
FOREIGN KEY(assigned_task_force_id) REFERENCES mtfs(id)
)""")

# mtfs
db.execute("""CREATE TABLE mtfs (
id INTEGER PRIMARY KEY,
name TEXT NOT NULL, -- eg. Epsilon-6
nickname TEXT NOT NULL, -- eg. "Village Idiots"
leader INTEGER, -- probably null when ripped from wikidot
active BOOLEAN DEFAULT TRUE NOT NULL,

FOREIGN KEY(leader) REFERENCES users(id)
)""")

# sites
db.execute("""CREATE TABLE sites (
id INTEGER PRIMARY KEY NOT NULL,
name TEXT NOT NULL,
director INTEGER,
FOREIGN KEY(director) REFERENCES users(id)
)""")

# audit log
db.execute("""CREATE TABLE audit_log (
id INTEGER PRIMARY KEY,
user_id INTEGER NOT NULL,
action TEXT NOT NULL, -- what happened (ie. login, file change, ect)
timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
details TEXT, -- optional additional details (eg. action description)

FOREIGN KEY(user_id) REFERENCES users(id)
)""")

