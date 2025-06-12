'''
Server for CS50x Final Project - SCiPNET
'''

import json
import socket
from utils import init_usr, db

# Set up a listening socket
HOST = "127.0.0.1" # localhost
PORT = 65432
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    print("Waiting for a connection . . .")
    s.listen() # listen for a connection
    conn, addr = s.accept() # accept connection
    print("Connection received")

    # Exchange data
    with conn:
        print(f"Connection from {addr}")
        while True:
            data = conn.recv(1024) # receive data
            # check for no data
            if not data:
                print("Connection terminated")
                break
            
            data = json.loads(data.decode()).split() # decode data
            print(f"Data received: {data}")

            # what did the user want to do
            if data[0] == "AUTH":
                print(f"Authenticating user {data[1]!r} with password: {data[2]!r}")
                # authenticate user
                row = db.execute("SELECT * FROM users WHERE id = ? AND password = ?", data[1], data[2])[0] # get the dict from row 0 (id is UNIQUE)
                if row: # sucess
                    print("Sucess")
                    usr = init_usr(row)
                    print(usr)
                    conn.sendall(json.dumps(True).encode())
                else: # failure
                    print("Failure")
                    conn.sendall(json.dumps(False).encode())
