'''
Server for CS50x Final Project - SCiPNET
'''

import json
import socket
from threading import activeCount, Thread
from utils import init_usr, db

# Information for server connection
HOST = "127.0.0.1" # localhost
PORT = 65432
ADDR = (HOST, PORT) # combine into a tuple

# TODO: Do I want this?
‫QUERIES‬ = { # dict to store all used sql queries, may remove
	"auth":"SELECT * FROM users WHERE id = ? AND password = ?"
}

def encode(data: any) -> any:
    # TODO: Validate
    '''
    Encodes data into json and converty it to bytes
    so it can be sent over a socket connection
    '''
    return json.dumps(data).encode()

def decode(data: any) -> any:
    # TODO: Validate
    '''
    decodes data received from a socket connection
    converts from bytes and json to list/str/int/ect
    '''
    return json.loads(data.decode()).split()

def auth_usr(id: int, password: str):
    # TODO: Validate
    '''
    authenticates a user by querying the deepwell
    '''
    print(f"Authenticating user {data[1]!r} with password: {data[2]!r}")
    
    # authenticate user
    row = db.execute(QUERIES["auth"], data[1], data[2])[0] # get the dict from row 0, all ids are unique
    if row: # sucess
    	print("Sucess")
    	usr = init_usr(row)
        print(usr)
        conn.sendall(encode(True))
    else: # failure
    	print("Failure")
        conn.sendall(encode(False))
        
def get_auth(c: socket.socket, limit: int = 3) -> (bool, int, str):
    # TODO: Validate
    # TODO: Transmit user data securely !!!!!!!!
    '''
    gets a client's authentication
    request limited: 3 by default
    returns id and password received, bool is if limit was exceeded
    '''
    for i in range(limit): # limit client auth requests
		c.sendall(encode("AUTH")) # request auth from client
		data = c.recv(1024) # receive auth
        if data: # no more loop if we received auth
            data = decode(data) # decode data
            return False, int(data[0]), data[1] # False, id, pw
    else: # request limit exceeded
        return True, 0, "" # True without id/pw

def handle_usr(client, addr):
    '''
    TODO: Implement logic
    1. Request auth
    2. validate auth
    if not valid:
    	log to "overwatch command"
        kick client
    while True:
    	get data request (file access, edit, ect)
        handle request
    '''
    exceeded, id, pw = get_auth(client)
    if exceeded:
        # TODO: Send client angry message and connection
        client.sendall(encode("INVALID"))
        return
    
    valid, usr = auth_usr(id, pw) # if valid, usr is a User class
    if not valid:
        client.sendall(encode("INVALID"))
    
    # fully authenticated
    client.sendall(encode("VALID"))
    
    # normal server-client back and forth
    while True:
        data = conn.recv(1024) # receive data
        # check for no data
        if not data:
            print("Connection terminated")
            break
                        
        data = decode() # decode data
        print(f"Data received: {data}")

		''' 
        TODO: what did the user want to do:
            * ACCESS file_ref
            	* SCP id/name | eg. 001 or SD Locke’s Proposal would be valid. 
                	NOTE: just accessing 001 would result in a random proposal, 
                    but if proposal is specified then use specified proposal
                * USER id/name | eg. 0 to access info for user with id 0, or full name to access that user
                    * Must have clearance equal to or above user
                * SITE id
                    * Accesses site directory, shows all staff, SCPs, MTFs, Director, site mission, other .txt’s
                * MTF id/name
                    * Generally not classified, but missions would be classified to scp clearance
        '''
        

def main():
    # TODO: Validate
    '''
    handles the mogic for the main thread:
    set up listening socket
    upon receiving a connection:
    	start thread with handle_usr
    '''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: # set up a listening socket
    	s.bind(ADDR)
        print("Waiting for a connection . . .")
    	s.listen() # listen for a connection
        while True: # for each connection
            conn, addr = s.accept() # accept it
            print(f"Connection from {addr}")
            thread = Thread(target=handle_usr, args=(conn, addr)) # init thread
            thread.start() # start thread
            print(f"Active connections: {activeCount() - 1}")
          
  
if __name__ == __main__:
    main()