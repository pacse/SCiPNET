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
                    conn.sendall(encode("CREATE SCP"))  # send create request to server
                    response = conn.recv(1024)

                    if not response: # sanity check
                        printc("[ERROR]: NO RESPONSE FROM SERVER")
                        continue

                    response = decode(response)  # decode server response

                    scp["id"] = input(f"ID (next: {response['id']}): ")
                    
                    printc("Clearance Levels:")
                    for c_level in response["clearance_levels"]:
                        print(f"{c_level['name']}")

                    scp["classification_level_id"] = int(input("Clearance Level: "))

                    printc("Containment Classes:")
                    for c_class in response["containment_classes"]:
                        print(f"{c_class['id']} - {c_class['name']}")

                    scp["containment_class_id"] = int(input("Containment Class: "))

                    printc("Disruption Classes:")
                    for d_class in response["disruption_classes"]:
                        print(f"{d_class['id']} - {d_class['name']}")

                    scp["disruption_class_id"] = int(input("Disruption Class: "))

                    printc("Risk Classes:")
                    for r_class in response["risk_classes"]:
                        print(f"{r_class['id']} - {r_class['name']}")

                    scp["risk_class_id"] = int(input("Risk Class: "))

                    scp["site_responsible_id"] = int(input("Site Responsible: "))

                    scp["assigned_task_force_id"] = input("Assigned Task Force (id): ")

                    scp["special_containment_procedures"] = input("Special Containment Procedures: ")

                    scp["description"] = input("Description: ")

                    conn.sendall(encode(scp)) # send scp data to server
                    response = conn.recv(1024)
            else:
                print("INVALID REQUEST")