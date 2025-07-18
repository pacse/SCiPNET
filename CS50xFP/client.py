'''
Client
'''

import socket
import sys
from rich.console import Console
from rich.markdown import Markdown

from utils import art
from utils.sql import init_usr
from utils.CSsocket import decode, recv, send

from utils.basic import clear
import utils.client as client

# enable/disable debug messages
DEBUG = False

# Quickstart for debugging
QS = True if len(sys.argv) == 3 else False


if __name__ == "__main__":
    with client.conn_to_server() as server:
        if not QS:
            art.startup()  # print startup screen
        console = Console() # console to display markdown

        # authenticate
        id = sys.argv[1] if QS else int(input("ID: ")) # get ID
        password = sys.argv[2] if QS else input("Password: ") # get PW

        send(server, f"AUTH {id} {password}") # send auth request to server
        result = recv(server) # receive reply from server
        
        if not result: # no data, some error happened
            art.printc("[ERROR]: NO RESPONSE FROM DEEPWELL")
            server.close()
            sys.exit()
        
        # we have data, decode it
        result = decode(result)

        if DEBUG: # debug flag
            print(f"Result: {result}")

        if result[0] == False: # invalid auth
            #TODO: prettify
            art.printc("INVALID AUTHORIZATION")
            art.printc("ACCESS DENIED")
            sys.exit()

        else: # valid auth
            usr = init_usr(result[1])
            art.login(usr)

        # main loop
        while True:
            request = input(">>> ") # get usr input
            split_request = request.upper().split()
            action = split_request[0]

            if action == "CREATE": # usr wants to create a file
                sucess = client.create(server, split_request[1], usr.clearance_level_id)

            elif action == "ACCESS": # usr wants to access a file
                sucess = client.access(server, console, split_request[1], split_request[2])

            elif action == "LOGOUT":
                print("Logging out...")
                server.close()
                break

            elif action in ["CLEAR", "CLS"]:
                clear()

            else:
                print("INVALID COMMAND")