'''
Server for CS50x Final Project - SCiPNET
'''

import socket
from dataclasses import asdict
from threading import active_count, Thread
from typing import cast
from sys import exit
from utils import ADDR, db, decode, encode, get_next_id, get_id
from utils import init_usr, log_event, User, RCVSIZE, send, recv
from urllib.parse import quote
from urllib.parse import unquote
import os

def auth_usr(id: int, password: str) -> tuple[bool, User | None]:
    # TODO: Validate
    '''
    Authenticates a user by querying the deepwell
    '''
    print(f"Authenticating user {id!r} with password: {password!r}")

    # authenticate user
    row = db.execute("SELECT * FROM users WHERE id = ? AND password = ?", id, password) # get the dict from row 0, all ids are unique
    if row: # sucess
        usr = init_usr(row[0])
        print(f"Sucess, returning: True, {usr}")
        return True, usr # return True and a User dataclass
    else: # failure
        print("Falure, returning: False, None")
        return False, None # return False and None for User dataclass
    

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

        print(f"Data: {data}")

        # ensure it was an auth request
        if not data or data[0] != "AUTH" or len(data) != 3:
            print(f"[THREAD {thread_id}] Invalid auth request: {data}")
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
                        * Accesses site directory, shows all staff, SCPs, MTFs, Director, site mission, other .txt's
                    * MTF id/name
                        * Generally not classified, but missions would be classified to scp clearance
                * CREATE action
            '''

            if data[0] == "CREATE":  # usr wants to create a file
                if data[1] == "SCP": # scp file TODO: Validate
                    response = {}
                    response["id"] = get_next_id('scps')
                    response["clearance_levels"] = db.execute("SELECT id, name FROM clearance_levels")
                    response["containment_classes"] = db.execute("SELECT id, name FROM containment_class")
                    response["disruption_classes"] = db.execute("SELECT id, name FROM disruption_class")
                    response["risk_classes"] = db.execute("SELECT id, name FROM risk_class")

                    send(client, response) # send client info for creating an SCP file

                    scp = recv(client) # get scp data
                    if not scp:
                        print(f"[THREAD {thread_id}] No data received, closing connection")
                        client.close()
                        return
                    scp = decode(scp)
                    print(f"[THREAD {thread_id}] SCP data received: {scp}")
                    scp["assigned_task_force_id"] = get_id("mtfs", scp["assigned_task_force_id"]) if scp["assigned_task_force_id"] else None
                    db.execute("""
                        INSERT INTO scps (id, classification_level_id, containment_class_id, secondary_class_id, disruption_class_id, risk_class_id, site_responsible_id, assigned_task_force_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, scp["id"], scp["classification_level_id"], scp["containment_class_id"], 0,  # secondary_class is not implemented yet
                        scp["disruption_class_id"], scp["risk_class_id"], scp["site_responsible_id"], scp["assigned_task_force_id"])
                    
                    with open(f"scp_{scp['id']}.txt", "w") as f:  # create scp file
                        f.write(f"Special Containment Procedures:\n{scp['special_containment_procedures']}\n")
                        f.write(f"Description:\n{scp['description']}\n")
                # TODO: Handle MTF Creation
                # TODO: Handle Site Creation
                elif data[1] == "SITE":
                    send(client, {"STATUS":"VALID"}) # make c happy
                    data = recv(client)
                    if not data:
                        client.close()
                        print(f"[THREAD {thread_id}] No data received from client, closed")
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
                            "status":"INVALID",
                            "error":"INVALID VALUES FOR name OR director"
                        })

                    # add to deepwell
                    try:
                        db.execute("INSERT INTO sites (name,director) VALUES (?,?)",
                                   data["name"], data["director"] if isinstance(
                                   data["director"],int) else get_id("users",
                                                                data["director"]))

                    except Exception as e:
                        send(client, {
                            "status":"INVALID",
                            "error":f"ERROR ADDING TO DEEPWELL: {e}"
                        })
                        continue

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
                            descs = {"desc test":"woohoo!"} # fname:data
                            with open(f"{path}/descs/main.md") as f:
                                descs["main"] = f.read()
                            
                            # SCPs
                            SCPs = {"SCP test":"woohoo!"}
                            with open(f"{path}/SCPs/main.md") as f:
                                SCPs["main"] = f.read()

                            # addenda 
                            # TODO: Get dynamically
                            addenda = {}
                            a_names = [
                                f"Addendum%20049.1%3A%20Discovery",
                                f"Addendum%20049.2%3A%20Observation%20Log",
                                f"Addendum%20049.3%3A%2004%2F16%2F2017%20Incident",
                                f"Addendum%20049.4%3A%20Post-Incident%20Report%20Interview"
                            ]
                            for name in a_names:
                                with open(f"{path}/addenda/{name}.md") as f:
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

def main():
    # TODO: Validate
    '''
    handles the logic for the main thread
    '''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server: # set up a listening socket
        server.bind(ADDR)
        print("Waiting for a connection . . .")
        server.listen() # listen for a connection
        while True: # for each connection
            try:
                conn, addr = server.accept() # accept it
                print(f"Connection from {addr}\n")
                thread = Thread(target=handle_usr, args=(conn, addr, active_count() - 1)) # init thread with zero-indexed thread id
                thread.start() # start thread
                print(f"Active connections: {active_count() - 1}")
            except KeyboardInterrupt:
                print("Exiting")
                exit()

if __name__ == "__main__":
    main()