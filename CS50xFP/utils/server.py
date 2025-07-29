'''
Server side utility functions
'''
import os
import socket
from typing import cast, Final as constant
from dataclasses import asdict
from pathlib import Path

from .sql import db, User, init_usr, log_event, get_id, next_id
from .socket import send, recv

# enable/disable debug messages
DEBUG = False

# valid file types (creatable/accessible)
VALID_F_TYPES = [
    "SCP",
    "MTF",
    "SITE",
    "USER",
]

# path to deepwell
CS50xFP_PATH: constant = Path(__file__).resolve().parent.parent # constant bc path isn't all upper case
DEEPWELL_PATH = CS50xFP_PATH / "deepwell"

def valid_f_type(check: str) -> bool:
    if check in VALID_F_TYPES:
        return True
    else:
        return False

def auth_usr(id: int, password: str) -> tuple[bool, User | None]:
    # TODO: Validate
    '''
    Authenticates a user by querying the deepwell
    '''
    if DEBUG:
        print(f"Authenticating user {id!r} with password: {password!r}")

    # authenticate user
    row = db.execute("SELECT * FROM users WHERE id = ? AND password = ?", id, password) # get the dict from row 0, all ids are unique
    if row: # sucess
        usr = init_usr(row[0])
        if DEBUG:
            print(f"Sucess, returning: True, {usr}")
        return True, usr # return True and a User dataclass
    else: # failure
        if DEBUG:
            print("Falure, returning: False, None")
        return False, None # return False and None for User dataclass


def create(client: socket.socket, f_type: str, thread_id: int, usr: User) -> None:
    
    # check if valid file type
    if not valid_f_type(f_type):
        send(client, ["INVALID FILETYPE", f_type])
        log_event(usr.id,
                  "USR TRIED TO CREATE A INVALID FILE TYPE",
                  f"ATTEMPTED TYPE: {f_type}")
        return

    # check high enough clearance lvl
    if f_type == "USER" and usr.clearance_level_id < 2:
        send(client, ["CLEARANCE TOO LOW", 2, usr.clearance_level_id])
        log_event(usr.id,
                  "USR TRIED TO CREATE A USER WITHOUT CLEARANCE",
                  f"HAS CLEARANCE {usr.clearance_level_id}, NEEDS CLEARANCE 2")
        return
    
    elif f_type == "SITE" and usr.clearance_level_id < 3:
        send(client, ["CLEARANCE TOO LOW", 3, usr.clearance_level_id])
        log_event(usr.id,
                  "USR TRIED TO CREATE A SITE WITHOUT CLEARANCE",
                  f"HAS CLEARANCE {usr.clearance_level_id}, NEEDS CLEARANCE 3")
        return

    # give use all clear to begin rendering
    send(client, "RENDER")

    # get necessary info for file creation
    if f_type == "SCP":
        info = {}
        info["id"] = next_id('scps')
        info["clearance_levels"] = db.execute("SELECT id, name FROM clearance_levels")
        info["containment_classes"] = db.execute("SELECT id, name FROM containment_classes")
        info["secondary_classes"] = db.execute("SELECT id, name FROM secondary_classes")
        info["disruption_classes"] = db.execute("SELECT id, name FROM disruption_classes")
        info["risk_classes"] = db.execute("SELECT id, name FROM risk_classes")

    elif f_type == "USER":
        info = {}
        # get clearance lvls
        info["clearance_levels"] = db.execute("SELECT id, name FROM clearance_levels")
        # get titles
        info["titles"] = db.execute("SELECT id, name FROM titles")

    else:
        info = "NONE"

    # send to usr
    send(client, info)

    # recv file
    file = recv(client)

    if not file:
        # tell client, log error, return
        send(client, "NO DATA RECEIVED")
        log_event(usr.id,
                  "NO FILE DATA RECEIVED DURING FILE CREATION")
        return
    
    # validate info
    try:
        if f_type == "SCP":
                # check types
                assert isinstance(file, dict)
                print("Is dict") # debug
                assert isinstance(file["id"], int)
                print("ID is int") # debug
                assert isinstance(file["classification_level_id"], int)
                print("Classification level is int") # debug
                assert isinstance(file["containment_class_id"], int)
                print("Containment class is int") # debug
                assert isinstance(file["secondary_class_id"], int)
                print("Secondary class is int") # debug
                assert isinstance(file["disruption_class_id"], int)
                print("Disruption class is int") # debug
                assert isinstance(file["risk_class_id"], int)
                print("Risk class is int") # debug
                assert isinstance(file["site_responsible_id"], int)
                print("Site responsible is int") # debug
                assert isinstance(file["atf_id"], (str, int))
                print("ATF ID is str or int")
                assert isinstance(file["SCPs"], str)
                print("SCPs is str")
                assert isinstance(file["desc"], str)
                print("Description is str") # debug

                # complete type annotations
                file = cast(dict[str, int | str], file)

                # check key: value pairs
                assert file["classification_level_id"] in range(1,next_id("clearance_levels"))
                print("classification_level_id is valid")
                assert file["containment_class_id"] in range(1,next_id("containment_classes"))
                print("containment_class_id is valid")
                assert file["secondary_class_id"] in range(0,next_id("secondary_classes"))
                print("secondary_class_id is valid")
                assert file["disruption_class_id"] in range(1, next_id("disruption_classes"))
                print("disruption_class_id is valid")
                assert file["risk_class_id"] in range(1, next_id("risk_classes"))
                print("risk_class_id is valid")
                assert file["site_responsible_id"] in range(0, next_id("sites"))
                print("site_responsible_id is valid")

                # make atf 'name' it's corresponding id if str
                if isinstance(file["atf_id"], str):
                    file["atf_id"] = get_id("mtfs", file["atf_id"])

                assert file["atf_id"] in range(0, next_id("mtfs"))
                print("atf_id is valid")

        elif f_type == "MTF":
            # check types and keys
            assert isinstance(file, dict)
            assert isinstance(file["name"], str)
            assert isinstance(file["nickname"], str)
            assert isinstance(file["leader"], int)
            assert isinstance(file["desc"], str)

            # complete type annotations
            file = cast(dict[str, int | str], file)

            # check key:value pair
            assert file["leader"] in range(1, next_id("users"))

        elif f_type == "SITE":
            # check types and keys
            assert isinstance(file, dict)
            assert isinstance(file["name"], str)
            assert isinstance(file["director"], int)
            assert isinstance(file["loc"], str)
            assert isinstance(file["desc"], str)
            assert isinstance(file["dossier"], str)

            # complete type annotations
            file = cast(dict[str, int | str], file)

            # check k:v pair
            assert file["director"] in range(1, next_id("users"))
    
        elif f_type == "USER":
            # check types and keys
            assert isinstance(file, dict)
            assert isinstance(file["name"], str)
            assert isinstance(file["password"], str)
            assert isinstance(file["clearance_level_id"], int)
            assert isinstance(file["title_id"], int)
            assert isinstance(file["site_id"], int)
            assert isinstance(file["override_phrase"], str)

            if file["override_phrase"] == "None":
                file["override_phrase"] = None

            # complete type annotations
            file = cast(dict[str, int | str | None], file)

            # check k:v pairs
            assert file["clearance_level_id"] in range(1, next_id("clearance_levels"))
            assert file["title_id"] in range(1, next_id("titles"))
            assert file["site_id"] in range(1, next_id("sites"))

    except (AssertionError, KeyError, IndexError):
        send(client, "INVALID FILE DATA")
        log_event(usr.id,
                    "INVALID FILE DATA RECEIVED DURING FILE CREATION",
                    str(file))
        return
        
    # YIPPEE! we got valid data 🎉
    print("File data is valid, proceeding...") # debug

    # try to insert into deepwell 
    # if get an error, tell usr
    try:
        if f_type == "SCP":
            db.execute("""INSERT INTO scps (id, classification_level_id,
                    containment_class_id, secondary_class_id, 
                    disruption_class_id, risk_class_id, site_responsible_id,
                    assigned_task_force_id) VALUES (?,?,?,?,?,?,?,?)""", 
                    file["id"], file["classification_level_id"], 
                    file["containment_class_id"], file["secondary_class_id"],
                    file["disruption_class_id"], file["risk_class_id"], 
                    file["site_responsible_id"], file["atf_id"])
        
        elif f_type == "MTF":
            db.execute("""INSERT INTO mtfs (name, nickname,
                    leader) VALUES (?,?,?)""", 
                    file["name"], file["nickname"], file["leader"])

        elif f_type == "SITE":
            db.execute("""INSERT INTO sites (name,director)
                       VALUES (?,?)""",
                       file["name"], file["director"])
            
        elif f_type == "USER":
            db.execute("""INSERT INTO users (name,password,
                       clearance_level_id,title_id,site_id,override_phrase)
                       VALUES (?,?,?,?,?,?)""",
                       file["name"], file["password"], 
                       file["clearance_level_id"], file["title_id"],
                       file["site_id"], file["override_phrase"])
    
    except ValueError as e:
        send(client, "INVALID FILE DATA")
        log_event(usr.id,
                    "INVALID FILE DATA RECEIVED DURING FILE CREATION",
                    str(file))
        return

    except Exception as e:
        log_event(usr.id, 
                  "ERROR INSERING INTO SQL DATABASE DURING FILE CREATION",
                  str(e))
        send(client, ["SQL ERROR", str(e)])
        return

    # TODO: create dirs & files
    try:
        # create main dir
        path = DEEPWELL_PATH / f"{f_type.lower()}s" / str(file['id'])
        os.makedirs(path)

        if f_type == "SCP":
            # create subdirs and populate with files
            os.makedirs(path / "descs")
            with open(path / "descs" / "main.md", "x") as f:
                f.write(cast(str, file["desc"]))

            os.makedirs(path / "SCPs")
            with open(path / "SCPs" / "main.md", "x") as f:
                f.write(cast(str, file["SCPs"]))

            os.makedirs(path / "addenda")
            # TODO: Handle addenda

        elif f_type == "MTF":
            with open(path / "desc.md", "x") as f:
                f.write(cast(str, file["desc"]))

        elif f_type == "SITE":
            with open(path / "loc.md", "x") as f:
                f.write(cast(str, file["loc"]))
            with open(path / "desc.md", "x") as f:
                f.write(cast(str, file["desc"]))
            with open(path / "dossier.md", "x") as f:
                f.write(cast(str, file["dossier"]))
            with open(path / "loc.md", "x") as f:
                f.write(cast(str, file["loc"]))

    except (FileExistsError, OSError) as e:
        # tried to create a dir that already exists, probably
        print(f"Error creating directory: {e}")
        send(client, "INVALID FILE DATA")
        return


    # send created message to client
    send(client, "CREATED")
    print("created file") # debug

def access(client: socket.socket, f_type: str, f_identifier: int | str, thread_id: int, usr: User) -> None:
    # TODO: validate
    # check if valid file type
    if not valid_f_type(f_type):
        send(client, ["INVALID FILETYPE", f_type])
        log_event(usr.id,
                  "USR TRIED TO ACCESS A INVALID FILE TYPE",
                  f"ATTEMPTED TYPE: {f_type}")
        return

    # try to get file from sql database
    try:
        # get id for f_id if f_id is str
        if isinstance(f_identifier, str):
            try: # try to convert to int
                if DEBUG:
                    print(f"Trying to convert {f_identifier!r} to int")
                f_identifier = int(f_identifier)

            except ValueError: # if not int, get id from db
                f_identifier = get_id(f"{f_type.lower()}s", f_identifier)
        
        # get file
        data = db.execute(f"SELECT * FROM {f_type.lower()}s WHERE id = ?", f_identifier)[0]
    except IndexError:
        send(client, "EXPUNGED")
        log_event(usr.id,
                  "USR TRIED TO ACCESS A EXPUNGED FILE",
                  f"ATTEMPTED FILE: {f_type} {f_identifier}")
        return
    
    # validate usr clearance
    if f_type == "USER" and\
    usr.clearance_level_id < data["clearance_level_id"]:
        send(client, ["REDACTED", data["clearance_level_id"], usr.clearance_level_id])
        log_event(usr.id,
                  f"USR TRIED TO ACCESS USR {f_identifier} WITHOUT CLEARANCE",
                  f"HAS CLEARANCE {usr.clearance_level_id}, NEEDS CLEARANCE {data['clearance_level_id']}")
        return
    
    elif f_type == "SCP" and\
    usr.clearance_level_id < data["classification_level_id"]:
        
        send(client, ["REDACTED", data["classification_level_id"], usr.clearance_level_id])
        log_event(usr.id,
                  f"USR TRIED TO ACCESS SCP {f_identifier} WITHOUT CLEARANCE",
                  f"HAS CLEARANCE {usr.clearance_level_id}, NEEDS CLEARANCE {data['clearance_level_id']}")
        return
    
    elif f_type == "SITE" and (
    usr.clearance_level_id < 3 or
    usr.site_id != f_identifier):
    # site access requirements: 
    # must work there OR
    # must be over clearance level 3
        send(client, ["REDACTED", 3, usr.clearance_level_id])
        log_event(usr.id,
                  f"USR TRIED TO ACCESS SITE {f_identifier} WITHOUT CLEARANCE",
                  f"HAS CLEARANCE {usr.clearance_level_id}, NEEDS CLEARANCE 3")
        return

    # YAY!!! 🎉 
    # We can build response
    response = {"db_info":data}

    # build path to file
    path = (DEEPWELL_PATH / f"{f_type.lower()}s" / str(f_identifier)).resolve()

    # get files from deepwell
    # NOTE: None for usr
    if f_type == "SCP":

        # get descs
        descs = {}
        descs_path = path / "descs"
        if descs_path.exists():
            for desc in os.listdir(descs_path):
                with open(descs_path / desc, "r", encoding="utf-8") as f:
                    descs[desc] = f.read()
        else:
            log_event(usr.id,
                        "USR TRIED TO ACCESS SCP WITHOUT DESC PATH",
                        f"ATTEMPTED SCP: {f_identifier}, PATH: {descs_path}")
            send(client, "INVALID FILE DATA")
        
        response["descs"] = descs

        # get SCPs
        scps = {}
        scps_path = path / "SCPs"
        if scps_path.exists():
            for scp in os.listdir(scps_path):
                with open(scps_path / scp, "r", encoding="utf-8") as f:
                    scps[scp] = f.read()
        else:
            log_event(usr.id,
                        "USR TRIED TO ACCESS SCP WITHOUT SCPs PATH",
                        f"ATTEMPTED SCP: {f_identifier}, PATH: {scps_path}")
            send(client, "INVALID FILE DATA")
        
        response["SCPs"] = scps

        # get addenda
        addenda = {}
        addenda_path = path / "addenda"
        if addenda_path.exists():
            for addendum in os.listdir(addenda_path):
                with open(addenda_path / addendum, "r", encoding="utf-8") as f:
                    addenda[addendum] = f.read()
        else:
            log_event(usr.id,
                        "USR TRIED TO ACCESS SCP WITHOUT ADDENDA PATH",
                        f"ATTEMPTED SCP: {f_identifier}, PATH: {addenda_path}")
            send(client, "INVALID FILE DATA")
        
        response["addenda"] = addenda
    
    elif f_type == "MTF":
        if path.exists():
            with open(path / "desc.md", "r", encoding="utf-8") as f:
                response["desc"] = f.read()
        else:
            log_event(usr.id,
                        "USR TRIED TO ACCESS MTF WITHOUT PATH",
                        f"ATTEMPTED MTF: {f_identifier}, PATH: {path}")
            send(client, "INVALID FILE DATA")
            return

    elif f_type == "SITE":
        if path.exists():
            with open(path / "loc.md", "r", encoding="utf-8") as f:
                response["loc"] = f.read()
            with open(path / "desc.md", "r", encoding="utf-8") as f:
                response["desc"] = f.read()
            with open(path / "dossier.md", "r", encoding="utf-8") as f:
                response["dossier"] = f.read()
        else:
            log_event(usr.id,
                        "USR TRIED TO ACCESS SITE WITHOUT PATH",
                        f"ATTEMPTED SITE: {f_identifier}, PATH: {path}")
            send(client, "INVALID FILE DATA")
            return
        
        # get personnel
        personnel = db.execute("SELECT id, name, title_id, clearance_level_id FROM users WHERE site_id = ?", f_identifier)
        # get scps
        scps = db.execute("""SELECT id, containment_class_id, secondary_class_id,
                          disruption_class_id, risk_class_id FROM scps 
                          WHERE site_responsible_id = ? and classification_level_id <= ?""",
                          f_identifier, usr.clearance_level_id)

        if personnel and scps:
            response["personnel"] = personnel
            response["scps"] = scps
        else:
            log_event(usr.id,
                        "USR TRIED TO ACCESS SITE WITHOUT PERSONNEL OR SCPS",
                        f"ATTEMPTED SITE: {f_identifier}")
            send(client, "INVALID FILE DATA")
            return
    
    # send response to client
    send(client, ["GRANTED", response])


def handle_usr(client: socket.socket, addr, thread_id: int) -> None:
    '''
    Function for threads after a user connects to the server
    '''
    try:
        # receive auth from client
        data = recv(client)

        if not data:
            print(f"[THREAD {thread_id}] ERROR: No auth received from client, closing connection")
            client.close()
            return
        
        split_data: list[str | int] = data.split() # decode data

        # validate types
        try:
            split_data[0] = str(split_data[0])
            split_data[1] = int(split_data[1])
            split_data[2] = str(split_data[2])
        except ValueError:
            print(f"[THREAD {thread_id}] ERROR: Invalid auth request: {split_data}")
            send(client, False)
            client.close()
            return

        if DEBUG:
            print(f"Data: {split_data}")

        # ensure it was an auth request
        if split_data[0] != "AUTH" or len(split_data) != 3:
            print(f"[THREAD {thread_id}] ERROR: Invalid auth request: {split_data}")
            send(client, False)
            client.close()
            return
        
        valid, usr = auth_usr(split_data[1], split_data[2]) # if valid, usr is a User class
        
        if not valid:
            send(client, (False, None))
            log_event(-1, "login", f"Failed login attempt from {addr[0]}:{addr[1]} with id {split_data[1]!r} and password {split_data[2]!r}") # log to audit log TODO: Null usr
            client.close()
            return
        else:
            usr = cast(User, usr) # tell type checking usr is a User class
        
        # fully authenticated
        print(f"[HANDLE USER] sending: (True, {asdict(usr)})")
        send(client, (True, asdict(usr)))
        log_event(usr.id, "login", f"User {usr.name} logged in from {addr[0]}:{addr[1]}") # log to audit log
        
        # normal server-client back and forth
        while True:
            try:
                data = recv(client) # receive data
            except ConnectionAbortedError: # return if connection is terminated
                print(f"[THREAD {thread_id}] Connection terminated")
                client.close() # close connection
                return
            
            if not data:
                print(f"[THREAD {thread_id}] No data received, closing connection")
                client.close()
                return
            else:
                split_data = data.split()

            print(f"[THREAD {thread_id}] Data received: {split_data}")

            ''' 
            TODO: what did the user want to do:
                * ACCESS file_ref
                    * SCP id/name | eg. 001 or SD Locke's Proposal would be valid. 
                        NOTE: just accessing 001 would result in a random proposal, 
                        but if proposal is specified then use specified proposal
                    * USER id/name | eg. 0 to access info for user with id 0, or full name to access that user
                        * Must have clearance equal to or above user
                    * SITE id
                        * Accesses site directory, shows all staff, SCPs, MTFs, Director, site mission, other .md's
                    * MTF id/name
                        * Generally not classified, but missions would be classified to scp lvl
                * CREATE action
            '''

            if split_data[0] == "CREATE":  # usr wants to create a file
                create(client, cast(str, split_data[1]), thread_id, usr)

            elif split_data[0] == "ACCESS":
                access(client, cast(str,split_data[1]), split_data[2], thread_id, usr)

    except Exception as e:
        client.close() # close connection
        raise e