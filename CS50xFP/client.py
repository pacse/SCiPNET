'''
Client
'''
import art
import socket
import sys
from utils import ADDR, decode, encode, get_next_id, init_usr, handle_reply, printc

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
            split_request = request.split()

            if split_request[0] == "CREATE":  # usr wants to create a file
                if split_request[1] == "SCP": # scp file
                    scp = {}
                    printc("CREATE SCP")
                    scp["id"] = input(f"ID (next: {get_next_id('scps')}): ")

                    printc("Clearance Levels:")
                    printc("Level 1 - Unrestricted")
                    printc("Level 2 - Restricted")
                    printc("Level 3 - Confidential")
                    printc("Level 4 - Secret")
                    printc("Level 5 - Top Secret")
                    printc("Level 6 - Cosmic Top Secret")
                    scp["classification_level_id"] = int(input("Clearance Level:"))

                    printc("Containment Classes:")
                    printc("1 - Safe")
                    printc("2 - Euclid")
                    printc("3 - Keter")
                    printc("4 - Neutralized")
                    printc("5 - Explained")
                    printc("6 - Decommissioned")
                    printc("7 - Pending")
                    printc("8 - Uncontained")
                    scp["containment_class_id"] = int(input("Clearance Level:"))

                    '''
                    sqlite> select id, name from containment_class;
                    +----+----------------+
                    | id |      name      |
                    +----+----------------+
                    | 1  | Safe           |
                    | 2  | Euclid         |
                    | 3  | Keter          |
                    | 4  | Neutralized    |
                    | 5  | Explained      |
                    | 6  | Decommissioned |
                    | 7  | Pending        |
                    | 8  | Uncontained    |
                    +----+----------------+
                    sqlite> select id, name from disruption_class;
                    +----+-------+
                    | id | name  |
                    +----+-------+
                    | 1  | Dark  |
                    | 2  | Vlam  |
                    | 3  | Keneq |
                    | 4  | Ekhi  |
                    | 5  | Amida |
                    +----+-------+
                    sqlite> select id, name from risk_class;
                    +----+----------+
                    | id |   name   |
                    +----+----------+
                    | 1  | Notice   |
                    | 2  | Caution  |
                    | 3  | Warning  |
                    | 4  | Danger   |
                    | 5  | Critical |
                    +----+----------+
                    sqlite> 
                    '''

            else:
                print("INVALID REQUEST")