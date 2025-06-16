'''
Client
'''
import art
import socket
import sys
from utils import ADDR, decode, encode, init_usr, handle_reply, printc

DEBUG = False


def conn_to_server(addr: tuple) -> socket.socket:
    '''
    Establishes connection to server
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(addr) # connect to server
    print("Connected . . .")
    return s


if __name__ == "__main__":
    with conn_to_server(ADDR) as conn:
        art.startup()  # print startup screen

        # authenticate
        id = int(input("ID: ")) # get ID
        password = input("Password: ") # get PW

        conn.sendall(encode(f"AUTH {id} {password}")) # send auth request to server
        print("Auth sent . . .")
        result = conn.recv(1024) # receive reply from server
        
        if not result: # no data, some error happened
            printc("[ERROR]: NO RESPONSE FROM DEEPWELL")
            sys.exit()
        
        # we have data, decode it
        result = decode(result)

        if DEBUG: # debug flag
            print(f"Result: {result}")

        if result[0] == False: # invalid auth
            printc("INVALID AUTHORIZATION\nACCESS DENIED")
            sys.exit()

        else: # valid auth
            usr = init_usr(result[1])
            art.login(usr)

        # main loop
        while True:
            request = input(">>> ") # get usr input

            conn.sendall(encode(request)) # send server request
            handle_reply(conn.recv(1024)) # handle reply