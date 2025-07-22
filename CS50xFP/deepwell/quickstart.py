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
name TEXT NOT NULL -- ie. Secret, Thaumiel, ect.
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
name TEXT NOT NULL -- eg. Safe, Euclid, Keter, ect.
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
name TEXT NOT NULL -- eg. Thaumiel, Appolyion, ect.
)""")

# basic init while not used
db.execute("INSERT INTO secondary_classes (id, name) VALUES (0, 'None')")

# disruption classes
db.execute("""CREATE TABLE disruption_classes (
id INTEGER PRIMARY KEY,
name TEXT NOT NULL -- eg. Dark, Vlam, ect.
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
name TEXT NOT NULL -- eg. Notice, Danger, ect.
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
name TEXT NOT NULL -- title (eg. site director, junior researcher, O5 council member)
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
site_responsible_id INTEGER,
assigned_task_force_id INTEGER,
status TEXT DEFAULT "active" CHECK(status IN ("active", "neutralized", "explained", "deleted")), -- Thanks ChatGPT for improving this from a bool :)

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

# === init old data ===
# site
db.execute("INSERT INTO sites (id, name) VALUES (1123, 'MEEEEE')")
# users
db.execute("INSERT INTO users (id, name, password, clearance_level_id, title_id, site_id, override_phrase) VALUES (?, ?, ?, ?, ?, ?, ?)",
           1, "Byankha (O5-4)", "DivIIne", 6, 8, 1123, "Lie until you aren't lying anymore.")
db.execute("INSERT INTO users (id, name, password, clearance_level_id, title_id, site_id, override_phrase) VALUES (?, ?, ?, ?, ?, ?, ?)",
           2, "Evren Packard", "InSAne", 5, 7, 1123, "You'll be living a life like Barbie and Ken")
db.execute("INSERT INTO users (id, name, password, clearance_level_id, title_id, site_id, override_phrase) VALUES (?, ?, ?, ?, ?, ?, ?)",
           3, "Glorbo Florbo", "1234", 3, 6, 1123, None)

# mtf
db.execute("INSERT INTO mtfs (id, name, nickname, leader) VALUES (?, ?, ?, ?)",
           1, "Gamma-94", "Gramma's little helpers", 3)

# scp
db.execute("INSERT INTO scps (id, classification_level_id, containment_class_id, secondary_class_id, disruption_class_id, risk_class_id, site_responsible_id, assigned_task_force_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
           49, 6, 2, 0, 2, 4, 1123, 1)

# == create indexes ==
indexes = [
    "CREATE INDEX idx_users_name ON users(name)",
    "CREATE INDEX idx_users_clearance_level_id ON users(clearance_level_id)",
    "CREATE INDEX idx_users_site_id ON users(site_id)",
    "CREATE INDEX idx_users_title_id ON  users(title_id)",
    "CREATE INDEX idx_scps_classification_level_id ON scps(classification_level_id)",
    "CREATE INDEX idx_scps_containment_class_id ON scps(containment_class_id)",
    "CREATE INDEX idx_scps_site_responsible_id ON scps(site_responsible_id)",
    "CREATE INDEX idx_scps_assigned_task_force_id ON scps(assigned_task_force_id)",
    "CREATE INDEX idx_scps_status ON scps(status)",
    "CREATE INDEX idx_mtfs_leader ON mtfs(leader)",
    "CREATE INDEX idx_sites_director ON sites(director)",
    "CREATE INDEX idx_audit_user_id ON audit_log(user_id)",
    "CREATE INDEX idx_audit_timestamp ON audit_log(timestamp)",
    "CREATE INDEX idx_clearance_levels_name ON clearance_levels(name)",
    "CREATE INDEX idx_containment_class_name ON containment_classes(name)",
    "CREATE INDEX idx_secondary_class_name ON secondary_classes(name)",
    "CREATE INDEX idx_disruption_class_name ON disruption_classes(name)",
    "CREATE INDEX idx_risk_class_name ON risk_classes(name)",
    "CREATE INDEX idx_titles_name ON titles(name)"
]
for index in indexes:
    db.execute(index)

print("Success puta madre!!!")