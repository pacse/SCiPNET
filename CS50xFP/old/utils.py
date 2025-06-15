from time import sleep
from os import system, scandir, name
import sqlite3
from cs50 import SQL


# Globals
imp = ""
db = SQL("sqlite:///SCiPNETdeepwell.db")

# Helper Functions
def get_name(table: str, id: int) -> str: # From the ducky :)
    row = db.execute("SELECT name FROM ? WHERE id = ?", table, id)
    return row[0]["name"]

def get_id(table: str, name: str) -> int:
    query = f"SELECT id FROM {table} WHERE name = ?"
    row = db.execute(query, name)
    return row[0]["id"]

def load_personell(site_id: int):
    row = db.execute("SELECT name FROM users WHERE id = (SELECT user_id FROM site_personnel WHERE site_id = ?)", site_id)
    return row[0]["name"]

def load_site_scps(site_id: int):
    row = db.execute("SELECT id FROM site_scps WHERE site_id = ?", site_id)
    return row[0]["id"]

# Get the next id in a table
def get_next_id(table: str):
    row = db.execute("SELECT MAX(id) + 1 as next_id FROM ?", table)
    return row[0]["next_id"]

# Clear the screen
def clear() -> None:
    # OS is windows
    if name == 'nt':
        system("cls")
    # OS is mac or linux (or any other I guess, it's an else statement...)
    else:
        system("clear")

# Log events in the audit log (eg. account creation, login, file access, file edit, ect.)
def log_event(user_id: int, action: str, details: str = "") -> None:
    db.execute("INSERT INTO audit_log (id, user_id, action, details) VALUES (?, ?, ?, ?)", get_next_id("audit_log"), user_id, action, details)

# Register a new user
def register_user(authorizer, auth_clearance: int) -> int:

    # Collect user information

    user_id = get_next_id("users")
    name = input("Name: ")
    password = input("Password: ")
    clearance = int(input("Clearance: "))
    if clearance >= auth_clearance and auth_clearance != 6:
        print(f"Warning: user {authorizer} can not grant level {clearance}.\nYour clearance has been set to {clearance - 1}.\nThis event has been logged.")
        log_event(user_id, f"User attempted to receive level {clearance} from {authorizer} (clearance level {auth_clearance})")
        clearance = auth_clearance - 1
    title = input("Title: ")
    title_id = get_id("titles", title)
    site = int(input("Assigned site: "))
    if clearance >= 3:
        phrase = input("Override phrase: ")
    else:
        phrase = None

    # Add new user to sql database

    db.execute("INSERT INTO users (id, name, password, clearance_level_id, title_id, site_id, phrase) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", user_id, name, password, clearance, title_id, site, phrase)

    # Log change
    log_event(authorizer, action = f"User {authorizer} registered user {user_id}")

    return user_id

# Login a user
def login(name, password):
    user = db.execute("SELECT * FROM users WHERE name = ?", name)
    user = user[0]

    if not user: # username incorrect
        print("User not found")
        return False

    if user["password"] != password: # password incorrect
        print("Password invalid")
        return False

    # user has been authenticated
    return True, user["id"]

# Verify a provided override phrase is greater than provided clearance
def verify_override_phrase(phrase, clearance) -> tuple[bool, int]:
    rows = db.execute("SELECT id, clearance_level_id FROM users WHERE phrase = ? AND clearance_level_id > ?", phrase, clearance)

    if rows:
        return True, int(rows[0]["id"])

    else:
        return False, -1

# Load a user's credentials
def load_credentials(user_id):
    row = db.execute("SELECT * FROM users WHERE id = ?", user_id)

    return row

# Print information about an SCP
def print_scp(scp):
    # Load SCP information

    # Get sql database info and print it
    scp_id = scp["id"]
    classification_level = get_name("clearance_levels", scp["classification_level_id"])
    containment_class = get_name("containment_classes", scp["containment_class_id"])
    secondary_class = get_name("secondary_classes", scp["secondary_class_id"])
    disruption_class = get_name("disruption_classes", scp["disruption_class_id"])
    risk_class = get_name("risk_classes", scp["risk_class_id"])
    site_responsible = get_name("sites", scp["site_responsible_id"])
    mtf = db.execute("SELECT name, nickname FROM mtfs WHERE id = ?", scp["assigned_task_force_id"])
    if mtf: # SCP has an assigned mtf
        # Combine name and nickname into one string (eg. Epsilon-6 "Village Idiots")
        assigned_mtf = mtf["name"] + '"' + mtf["nickname"] + '"' # From the duck
    else:
        assigned_mtf = "None"

    print(f"ID: {scp_id}", end=" ")
    print(f"Classified level {classification_level}")
    print(f"Containment Class: {containment_class}")
    if secondary_class != "":
        print(f"Secondary Class: {secondary_class}")
    print(f"Disruption Class: {disruption_class}")
    print(f"Risk Class: {risk_class}")
    print(f"Site Responsible: {site_responsible}")
    print(f"Assigned MTF: {assigned_mtf}")
    
    # Get rest of info from text files
    #go to scp directory
    directory = "Deepwell_Server/SCPs/" + scp["id"]
    #loop through all files
    for filename in scandir(directory):
        with open(filename) as file:
            contents = file.read()
            print(f"{filename.name}:\n{contents}") #filename.name from the duck

def access_scp(user_id, scp_id, clearance):
    scp = db.execute("SELECT * FROM scps WHERE id = ?", scp_id)

    if scp: #scp found
        scp_clearance = scp["classification_level_id"]
        if scp_clearance <= clearance:
            print("Access Granted")
            log_event(user_id, f"File SCP-{scp_id} accessed by user")
            print_scp(scp)

        else:
            log_event(user_id, f"User attempted to access SCP-{scp_id}", f"Did not meet clearance level (needed level {scp_clearance}, has level {clearance})")
            print("Clearance Denied. Required clearance:", scp_clearance)
            while True:
                imp = input("Please enter override phrase or nothing to abort\n>>> ")
                is_verified, authorizer = verify_override_phrase(imp, scp["Clearance"])
                if is_verified:
                    log_event(authorizer, f"User overrode clearance of user {user_id}")
                    log_event(user_id, f"User accessed file SCP-{scp_id} after an override by user {authorizer}")
                    print_scp(scp)

                elif imp == "":
                    return

                else:
                    print("Override phrase denied")
    else:
        print("File not found")
        return

def edit_scp(user_id, scp_id, clearance):
    scp = db.execute("SELECT * FROM scps WHERE id = ?", scp_id)

    if scp:
        scp_clearance = scp["classification_level_id"]
        if scp_clearance <= clearance:
            print("Access Granted")

            check = input(f"Are you sure you would like to edit file SCP-{scp_id}? (y/n)\n>>> ")
            if check == "y":
                log_event(user_id, f"File SCP-{scp_id} accesed by user in edit mode")
                print_scp(scp)

                # Actually edit
                print(f"Editing SCP-{scp_id}. Enter done to save all changes and exit edit mode")
                while True:
                    field = input("What would you like to edit?\n>>> ")
                    if field in scp:
                        new_value = input("What would you like to change it to?\n>>> ")
                        scp[field] = new_value
                        print("Edit saved (temporarily)")

                    elif field.lower() == "done":
                        # Commit all changes
                        print("Commiting changes...")
                        # SQL update
                        db.execute("UPDATE scps classification_level_id = ? containment_class_id = ? secondary_class_id = ? disruption_class_id = ? risk_class_id = ? site_responsible_id = ? assigned_task_force_id = ?, archived = ?",
                                   scp["classification_level_id"],
                                   scp["containment_class_id"],
                                   scp["secondary_class_id"],
                                   scp["disruption_class_id"],
                                   scp["risk_class_id"],
                                   scp["site_responsible_id"],
                                   scp["assigned_task_force_id"],
                                   scp["archived"]
                                   )
                        # File update
                        # Go to SCP directory
                        directory = "Deepwell_Server/" + scp["id"]
                        #loop through all files
                        for filename in scandir(directory):
                            with open(filename, "w") as file:
                                new_contents = scp[file.name] # Get new file contents
                                file.write("")
                                file.write(new_contents)
                    else:
                        print("Field not found")

def access_mtf(user_id, mtf_name):
    log_event(user_id, f"File MTF {mtf_name} accessed by user")
    print(f"Acessing file for MTF {mtf_name}")
    # Get info from sql table
    mtf = db.execute("SELECT * IN mtfs WHERE name = ?", mtf_name)

    id = mtf["id"]
    name = mtf["name"]
    nickname = mtf["nickname"]
    leader_id = mtf["leader"]
    leader_name = get_name("users", leader_id)
    active = mtf["active"]

    # Get info from file
    with open(f"Deepwell_Server/MTFs/{id}.txt") as file:
        description = file.read()

    print(f"ID: {id}")
    print(f"Name: {name}")
    print(f"Nickname: {nickname}")
    print(f"Leader: {leader_name}")
    print(f"Active: {active}")
    print(description)

def access_user(user_id, user_name):
    log_event(user_id, f"File user {user_name} accessed by user")
    print(f"Acessing file for user {user_name}")
    # Get info from sql table
    user = db.execute("SELECT * IN users WHERE name = ?", user_name)

    id = user["id"]
    name = user["name"]
    clearance_level = get_name("users", user["clearance_level_id"])
    title = get_name("titles", user["title_id"])
    site = user["site_id"]
    last_login = user["last_login"]

    # Get info from file
    with open(f"Deepwell_Server/Users/{id}.txt") as file:
        description = file.read()

    print(f"ID: {id}")
    print(f"Name: {name}")
    print(f"Title: {title}")
    print(f"Clearance level: {clearance_level}")
    print(f"Assigned site: {site}")
    print(f"Last login: {last_login}")
    print(description)

def access_site(user_id, site_id):
    log_event(user_id, f"File site-{site_id} accessed by user")
    print(f"Acessing file for site{site_id}")
    # Get info from sql table
    site = db.execute("SELECT * IN sites WHERE id = ?", site_id)

    director = get_name("users", site["director"])
    personell = load_personell(site_id)
    scps = load_site_scps(site_id)

    # Get info from file
    with open(f"Deepwell_Server/Sites/{site_id}.txt") as file:
        description = file.read()

    print(f"ID: {site_id}")
    print(f"Site Director: {director}")
    print(f"Site Personell:\n{personell}")
    print(f"Site SCP's:\n{scps}")
    print(description)

def get_help():
    # Get every command
    rows = db.execute("SELECT * FROM commands")
    # Print commands
    print("Commands:")
    for row in rows:
        print(row["command"], ":", row["description"])

# Process the given command
def process_command(imp, user_id, title, name, clearance):

    # Clear the screen
    if imp[0] == "clear":
        clear()
        return True

    # Display help info
    elif imp[0] == "help":
        get_help() # Somebody please, I'm loosing my sanity! 12/27/2024
        return True

    # Access a file article
    elif imp[0].lower() == "access":
        if imp[1].lower() == "scp":
            access_scp(user_id, imp[2], clearance)
            return True

        elif imp[1].lower() == "mtf":
            access_mtf(user_id, imp[2])

        elif imp[1].lower() == "user":
            access_user(user_id, imp[2])

    # Edit an SCP article
    elif imp[0] == "edit":
        edit_scp(user_id, imp[1], clearance)
        return True

    elif imp[0] == "logout":
        # logout user
        print("Logging out...")
        sleep(1)
        print(f"Logged out. Thank you {title} {name}")
        return False

    # Command not recognized
    else:
        print("Command either not recognized or not implemented")
        return True