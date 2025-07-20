'''
Server for CS50x Final Project - SCiPNET
'''

import socket
from threading import active_count, Thread

from utils.server import handle_usr
from utils.socket import ADDR

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
                print(f"Connection from {addr[0]}:{addr[1]}, Thread ID: {active_count() - 1}")
                thread = Thread(target=handle_usr, args=(conn, addr, active_count() - 1)) # init thread with zero-indexed thread id
                thread.start() # start thread
                print(f"Active connections: {active_count() - 1}")
            except KeyboardInterrupt:
                print("Exiting")
                return

if __name__ == "__main__":
    main()