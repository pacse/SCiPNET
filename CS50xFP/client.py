'''
Client
'''

import json
import socket
import sys

HOST = "127.0.0.1"
PORT = 65432

def conn_to_server(host: str, port: int) -> socket.socket:
    '''
    Establishes connection to server
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port)) # connect to server
    print("Connected . . .")
    return s


def auth_usr(s: socket.socket, id: int, password: str) -> bool:
    '''
    Authenticates a user with id and password
    assuming a connection on s
    '''
    s.sendall(json.dumps(f"AUTH {id} {password}").encode()) # try to auth user
    print("Auth sent . . .")
    result = s.recv(1024) # receive reply from server

    if not result: # no data, some error happened
        print("Server did respond")
        return False
    
    result = json.loads(result.decode()) # decode it
    
    if result == False:
        print("Incorrect id or password")
        return False
    else:
        print("User Authenticated")
        return True
    

with conn_to_server(HOST, PORT) as s:

    # try to authenticate user
    if not auth_usr(s, 1, "DivIIne"):
        sys.exit