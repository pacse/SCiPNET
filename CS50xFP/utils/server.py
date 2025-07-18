'''
Server side utility functions
'''
import os
import socket
from typing import cast
from dataclasses import asdict
from urllib.parse import quote, unquote

from .sql import db, User, init_usr, log_event, next_id, get_id
from .CSsocket import send, recv, decode

# enable/disable debug messages
DEBUG = True

VALID_F_TYPES = [
    "SCP",
    "MTF",
    "SITE",
    "USER",
]

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
    ''' # TODO: Handle SCP Creation
    if type == "SCP":
        try:
            # build necessary data
            response = {}
            response["id"] = get_next_id('scps')
            response["clearance_levels"] = db.execute("SELECT id, name FROM clearance_levels")
            response["containment_classes"] = db.execute("SELECT id, name FROM containment_class")
            response["secondary_classes"] = db.execute("SELECT id, name FROM secondary_class")
            response["disruption_classes"] = db.execute("SELECT id, name FROM disruption_class")
            response["risk_classes"] = db.execute("SELECT id, name FROM risk_class")

            send(client, response) # send client info for creating an SCP file

            data = recv(client) # get scp data
            if not data:
                print(f"[THREAD {thread_id}] No data received, closing connection")
                client.close()
                return
            
            scp = decode(data)

            # check types
            try:
                assert isinstance(scp, dict)
                assert isinstance(scp["id"], int)
                assert isinstance(scp["classification_level_id"], str)
                assert isinstance(scp["containment_class_id"], int)
                assert isinstance(scp["secondary_class_id"], int)
                assert isinstance(scp["id"], int)
                assert isinstance(scp["id"], int)
                assert isinstance(scp["atf_id"], (str | None))

            except AssertionError:
                send(client, {
                    "status":"ERROR",
                    "error":"INVALID VALUES"
                })
                return
            
            print(f"[THREAD {thread_id}] SCP data received: {scp}")
            
            # create sql entry
            try:
                db.execute("""
                    INSERT INTO scps (id, classification_level_id, containment_class_id, 
                    secondary_class_id, disruption_class_id, risk_class_id, 
                    site_responsible_id, assigned_task_force_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""", 
                    scp["id"], scp["classification_level_id"], scp["containment_class_id"], 
                    scp["secondary_class_id"], scp["disruption_class_id"], scp["risk_class_id"], 
                    scp["site_responsible_id"], scp["atf_id"])
            
            except Exception as e:
                send(client, {
                    "status":"ERROR ADDING TO DEEPWELL",
                    "error":e
                })
            
            # create files
            path = f"./deepwell/scp/{scp['id']}" # TODO: leading 0's

            # directories
            os.makedirs(path, exist_ok=True)
            os.makedirs(f"{path}/addenda", exist_ok=True)
            os.makedirs(f"{path}/descs", exist_ok=True)
            os.makedirs(f"{path}/scps", exist_ok=True)

            # SCPs
            with open(f"{path}/SCPs/main.md", "w") as f:
                f.write(scp["SCPs"])
            
            # descs
            with open(f"{path}/descs/main.md", "w") as f:
                f.write(scp["desc"])
            
            # give client all clear
            send(client, {"status":"SUCESS"})
        
        except Exception as e:
            # send error to client
            send(client, {"status":"ERROR","error":e})

    # TODO: Handle MTF Creation
    elif type == "MTF":
        send(client, {"status":"VALID"})
        data = recv(client)

        if not data:
            client.close()
            print(f"[THREAD {thread_id}] No data received from client, connection closed")
            return
        
        mtf = decode(data)

        # check types
        try:
            assert isinstance(mtf, dict)
            assert isinstance(mtf["name"], str)
            assert isinstance(mtf["nickname"], str)
            assert isinstance(mtf["leader"], int)
            assert isinstance(mtf["desc"], str)
        except AssertionError:
            send(client, {
                "status":"ERROR",
                "error":"INVALID VALUES"
            })
            return
        
        # create sql entry
        try:
            db.execute("""INSERT INTO mtfs (name, nickname, 
                       leader) VALUES (?,?,?)""", mtf["name"], 
                       mtf["nickname"], mtf["leader"])
        except Exception as e:
            send(client, {
                "status":"ERROR ADDING TO DEEPWELL",
                "error":e
            })
            return
        
        id = db.execute("")
        
        # create files
        path = f"./deepwell/mtfs/{scp['id']}"

    # TODO: Handle Site Creation
    elif type == "SITE":
        send(client, {"status":"VALID"})
        data = recv(client)

        if not data:
            client.close()
            print(f"[THREAD {thread_id}] No data received from client, connection closed")
            return
        
        data = decode(data)

        # check types
        try:
            assert isinstance(data, dict)
            assert isinstance(data["name"], str)
            assert isinstance(data["director"], str | int)
            assert isinstance(data["loc"], str)
            assert isinstance(data["desc"], str)
        except AssertionError:
            send(client, {
                "status":"ERROR",
                "error":"INVALID VALUES"
            })
            return

        # add to deepwell
        try:
            db.execute("INSERT INTO sites (name,director) VALUES (?,?)",
                        data["name"], data["director"] if isinstance(
                        data["director"],int) else get_id("users",
                                                    data["director"]))

        except Exception as e:
            send(client, {
                "status":"ERROR ADDING TO DEEPWELL",
                "error":e
            })

        # create files
        path = f"./deepwell/sites/{quote(data['name'])}"
        os.makedirs(path, exist_ok=True)
        with open(f"{path}/loc.md", "w") as f:
            f.write(data["loc"])
        with open(f"{path}/desc.mc", "w") as f:
            f.write(data["desc"])
        
        # give client all clear
        send(client, {"status":"SUCESS"})

    # TODO: Handle User Creation
    elif type == "USER":
        
        send(client, {"status":"VALID"})
        data = recv(client)

        if not data:
            client.close()
            print(f"[THREAD {thread_id}] No data received from client, connection closed")
            return
        
        data = decode(data)

        # ensure high enough clearance
        if c_lvl < 3:
            send(client, {
                "status":"ERROR",
                "error":"Clearance level too low"
            })

        # check types
        try:
            assert isinstance(data, dict)
            assert isinstance
        except AssertionError:
            send(client, {
                "status":"ERROR",
                "error":"Invalid Values"
            })

    # invalid file type
    else:
        send(client, {"status":"INVALID"})
'''
    
    # check if valid file type
    if f_type not in VALID_F_TYPES:
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
        info["containment_classes"] = db.execute("SELECT id, name FROM containment_class")
        info["secondary_classes"] = db.execute("SELECT id, name FROM secondary_class")
        info["disruption_classes"] = db.execute("SELECT id, name FROM disruption_class")
        info["risk_classes"] = db.execute("SELECT id, name FROM risk_class")

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

    # decode file
    try:
        assert file is not None
        file = decode(file)
    except AssertionError:
        send(client, "NO DATA RECEIVED")
        log_event(usr.id,
                  "NO FILE DATA RECEIVED DURING FILE CREATION")
        return

    # validate info
    if f_type == "SCP":
        try:
            # check types
            assert isinstance(file, dict)
            assert isinstance(file["id"], int)
            assert isinstance(file["classification_level_id"], int)
            assert isinstance(file["containment_class_id"], int)
            assert isinstance(file["secondary_class_id"], int)
            assert isinstance(file["disruption_class_id"], int)
            assert isinstance(file["risk_class_id"], int)
            assert isinstance(file["site_responsible_id"], int)
            assert isinstance(file["atf_id"], (str, int))
            assert isinstance(file["SCPs"], str)
            assert isinstance(file["desc"], str)

            # complete type annotations
            file = cast(dict[str, int | str], file)

            # check key: value pairs
            assert file["classification_level_id"] in range(1,next_id("clasification_levels"))
            assert file["containment_class_id"] in range(1,next_id("containment_class"))
            assert file["secondary_class_id"] in range(1,next_id("secondary_class"))
            assert file["disruption_class_id"] in range(1, next_id("disruption_class"))
            assert file["risk_class_id"] in range(1, next_id("risk_class"))
            assert file["site_responsible_id"] in range(1, next_id("sites"))

            # make atf 'name' it's corresponding id if str
            if isinstance(file["atf_id"], str):
                file["atf_id"] = get_id("mtfs", file["atf_id"])

            assert file["atf_id"] in range(1, next_id("mtfs"))

        except AssertionError or KeyError or IndexError:
            send(client, "INVALID FILE DATA")
            log_event(usr.id,
                      "INVALID FILE DATA RECEIVED DURING FILE CREATION",
                      str(file))
            return

    elif f_type == "MTF":
        try:
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
        except AssertionError or KeyError or IndexError:
            send(client, "INVALID FILE DATA")
            log_event(usr.id,
                      "INVALID FILE DATA RECEIVED DURING FILE CREATION",
                      str(file))
            return

    elif f_type == "SITE":
        try:
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

        except AssertionError or KeyError or IndexError:
            send(client, "INVALID FILE DATA")
            log_event(usr.id,
                      "INVALID FILE DATA RECEIVED DURING FILE CREATION",
                      str(file))
            return
    
    elif f_type == "USER":
        try:
            # check types and keys
            assert isinstance(file, dict)
            assert isinstance(file["name"], str)
            assert isinstance(file["password"], str)
            assert isinstance(file["clearance_level_id"], int)
            assert isinstance(file["title_id"], int)
            assert isinstance(file["site_id"], int)
            assert isinstance(file["phrase"], str)

            if file["phrase"] == "None":
                file["phrase"] = None

            # complete type annotations
            file = cast(dict[str, int | str | None], file)

            # check k:v pairs
            assert file["clearance_level_id"] in range(1, next_id("clearance_levels"))
            assert file["title_id"] in range(1, next_id("titles"))
            assert file["site_id"] in range(1, next_id("sites"))

        except AssertionError or KeyError or IndexError:
            send(client, "INVALID FILE DATA")
            log_event(usr.id,
                      "INVALID FILE DATA RECEIVED DURING FILE CREATION",
                      str(file))
            return
        
    # YIPPEE! we got valid data 🎉

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
                    file["site_responsible_id"], file["assigned_task_force_id"])
        
        elif f_type == "MTF":
            db.execute("""INSERT INTO mtfs (id, name, nickname,
                    leader) VALUES (?,?,?,?)""", next_id("mtfs"), 
                    file["name"], file["nickname"], file["leader"])

        elif f_type == "SITE":
            db.execute("""INSERT INTO sites (id,name,director)
                       VALUES (?,?,?)""", next_id("sites"),
                       file["name"], file["director"])
            
        elif f_type == "USER":
            db.execute("""INSERT INTO users (id,name,password,
                       clearance_level_id,title_id,site_id,phrase)
                       VALUES (?,?,?,?,?,?,?)""", next_id("users"),
                       file["name"], file["password"], 
                       file["clearance_level_id"], file["title_id"],
                       file["site_id"], file["phrase"])

    except Exception as e:
        log_event(usr.id, 
                  "ERROR INSERING INTO SQL DATABASE DURING FILE CREATION",
                  str(e))
        send(client, ["SQL ERROR", e])
        return

    # TODO: create dirs & files

def access():
    pass

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
        
        data = decode(data).split() # decode data

        if DEBUG:
            print(f"Data: {data}")

        # ensure it was an auth request
        if not data or data[0] != "AUTH" or len(data) != 3:
            print(f"[THREAD {thread_id}] ERROR: Invalid auth request: {data}")
            send(client, False)
            client.close()
            return
        
        valid, usr = auth_usr(data[1], data[2]) # if valid, usr is a User class
        
        if not valid:
            send(client, (False, None))
            log_event(data[1], "login", f"Failed login attempt from {addr[0]}:{addr[1]} with id {data[1]!r} and password {data[2]!r}") # log to audit log
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

            data = decode(data).split() # decode data
            print(f"[THREAD {thread_id}] Data received: {data}")

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

            if data[0] == "CREATE":  # usr wants to create a file
                create(client, data[1], thread_id, usr)

            elif data[0] == "ACCESS":
                if data[1] == "SCP":
                    # query db for scp
                    try:
                        scp = db.execute("SELECT * FROM scps WHERE id = ?", int(data[2]))[0]
                    # data[2] not int or nothing from db
                    except ValueError | IndexError:
                        send(client, "EXPUNGED") # TODO: FIX EXPUNGED
                    else:
                        # check clearance
                        if usr.clearance_level_id < scp["classification_level_id"]:
                            # information for art.redacted()
                            response = {
                                "status":"REDACTED",
                                "f_classification":scp['classification_level_id'],
                                "usr_clearance":usr.clearance_level_id
                            }
                            send(client, response)
                        else:
                            # Usr can access SCP!!!
                            
                            # get external files
                            path = f"./deepwell/scps/{data[2]}"

                            # descriptions
                            descs = {} # fname:data
                            # get all files
                            d_names = os.listdir(f"{path}/descs")
                            for name in d_names:
                                with open(f"{path}/descs/{name}") as f:
                                    descs[name] = f.read()

                            # SCPs
                            SCPs = {}
                            SCP_names = os.listdir(f"{path}/SCPs")
                            for name in SCP_names:
                                with open(f"{path}/SCPs/{name}") as f:
                                    SCPs[name] = f.read()

                            # addenda 
                            # TODO: Get dynamically
                            addenda = {}
                            a_names = os.listdir(f"{path}/addenda")
                            for name in a_names:
                                with open(f"{path}/addenda/{name}") as f:
                                    addenda[name] = f.read()
                            
                            # Now we have all files, build response
                            response = {
                                "status":"GRANTED",
                                "scp_info":scp,
                                "descs":descs,
                                "SCPs":SCPs,
                                "addenda":addenda
                            }
                            # and send :)
                            send(client, response)

                # TODO: Handle MTF Access
                # TODO: Handle Site Access
                # TODO: Handle User Access
    except Exception as e:
        client.close() # close connection
        raise e
