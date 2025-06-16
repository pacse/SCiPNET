'''
Server for CS50x Final Project - SCiPNET
'''

import socket
from dataclasses import asdict
from threading import active_count, Thread
from typing import cast
from sys import exit
from utils import ADDR, db, decode, encode, init_usr, log_event, printc, User


def auth_usr(id: int, password: str) -> tuple[bool, User | None]:
    # TODO: Validate
    '''
    Authenticates a user by querying the deepwell
    '''
    print(f"Authenticating user {id!r} with password: {password!r}")

    # authenticate user
    row = db.execute("SELECT * FROM users WHERE id = ? AND password = ?", id, password)[0] # get the dict from row 0, all ids are unique
    if row: # sucess
        usr = init_usr(row)
        print(f"Sucess, returning: True, {usr}")
        return True, usr # return True and a User dataclass
    else: # failure
        print("Sucess, returning: False, None")
        return False, None # return False and None for User dataclass
    

def handle_usr(client: socket.socket, addr, thread_id: int) -> None:
    '''
    Function for threads after a user connects to the server
    TODO: handle request
    '''
    # receive auth from client
    data = client.recv(1024)
    data = decode(data).split() # decode data

    print(f"Data: {data}")

    # ensure it was an auth request
    if not data or data[0] != "AUTH" or len(data) != 3:
        print(f"[THREAD {thread_id}] Invalid auth request: {data}")
        client.sendall(encode(False))
        return
    
    valid, usr = auth_usr(data[1], data[2]) # if valid, usr is a User class
    if not valid:
        client.sendall(encode((False, None)))
        log_event(data[1], "login", f"Failed login attempt from {addr[0]}:{addr[1]} with id {data[1]!r} and password {data[2]!r}") # log to audit log
        return
    else:
        usr = cast(User, usr) # tell type checking usr is a User class
    
    # fully authenticated
    print(f"[HANDLE USER] sending: (True, {asdict(usr)})")
    client.sendall(encode((True, asdict(usr))))
    log_event(usr.id, "login", f"User {usr.name} logged in from {addr[0]}:{addr[1]}") # log to audit log
    
    # normal server-client back and forth
    while True:
        try:
            data = client.recv(1024) # receive data
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
            if data[1] == "SCP": # scp file
            	# get column names
            	columns = db.execute("SELECT * FROM scps WHERE id = -1")[0].keys() # row -1 is blank, get all keys
            	scp = {}
            	printc("CREATE SCP")
				for column in columns:
                    scp[column] = input(f"{column}: ")
                db.execute("INSERT INTO scps VALUES (?, ?, ?, )", scp[id], scp[])

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