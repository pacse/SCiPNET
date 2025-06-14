'''
Client
'''

import json
import socket
import sys
from utils import clear, printc, timestamp

HOST = "127.0.0.1"
PORT = 65432


# redacted message
def redacted(file: str) -> None:
  '''
  prints a message saying {file} is above your clearance
  art by ChatGPT
  '''
  lines = [
      "╔══════════════════════════════╗",
      "║        ACCESS DENIED         ║",
      "╚══════════════════════════════╝",
      "",
      f"FILE_REF: {file} ACCESS DENIED",
      "CLEARANCE LEVEL 6 - COSMIC TOP SECRET REQUIRED",
      "(YOU ARE CLEARANCE LEVEL 5 - TOP SECRET)",
      f"Logged to Overwatch Command at {timestamp()}",
  ]

  [printc(line) for line in lines]

# data expunged message
def expunged(file: str) -> None:
  '''
  prints a message saying {file} has been expunged
  art by ChatGPT
  '''
  lines = [
      "╔══════════════════════════════╗",
      "║        DATA EXPUNGED         ║",
      "╚══════════════════════════════╝",
      "",
      f"FILE_REF: {file} NOT FOUND",
      f"Logged to Overwatch Command at {timestamp()}",
  ]

  [printc(line) for line in lines]

# access granted message
def granted(file: str) -> None:
  '''
  prints a message saying access has been granted to a file
  art by ChatGPT
  '''
  lines = [
      "╔══════════════════════════════╗",
      "║        ACCESS GRANTED        ║",
      "╚══════════════════════════════╝",
      "",
      f"FILE_REF: {file} ACCESS GRANTED",
      f"Logged to Overwatch Command at {timestamp()}",
  ]

  [printc(line) for line in lines]


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


def main() -> None:
    '''
    Main function to run the client
    '''
    print("Connecting to server . . .")
    
    # connect to server
    with conn_to_server(HOST, PORT) as s:
        # try to authenticate user
        if not auth_usr(s, 1, "DivIIne"):
            sys.exit("Authentication failed")
        
        print("Welcome to SCiPNET Client")

if __name__ == "__main__":
    main()