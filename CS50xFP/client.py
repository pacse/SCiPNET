'''
Client
'''
import art
import socket
import sys
from utils import ADDR, RCVSIZE, decode, display_scp, encode, init_usr, printc, recv, send
from rich.console import Console
from rich.markdown import Markdown

DEBUG = False

# Quickstart for debugging
QS = True if len(sys.argv) == 3 else False


def conn_to_server(addr: tuple[str, int]) -> socket.socket:
    '''
    Establishes connection to server
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(addr) # connect to server
    print("Connected . . .")
    return s

if __name__ == "__main__":
    with conn_to_server(ADDR) as server:
        if not QS:
            art.startup()  # print startup screen
        console = Console() # console to display markdown

        # authenticate
        id = sys.argv[1] if QS else int(input("ID: ")) # get ID
        password = sys.argv[2] if QS else input("Password: ") # get PW

        send(server, f"AUTH {id} {password}") # send auth request to server
        result = recv(server) # receive reply from server
        
        if not result: # no data, some error happened
            printc("[ERROR]: NO RESPONSE FROM DEEPWELL")
            server.close()
            sys.exit()
        
        # we have data, decode it
        result = decode(result)

        if DEBUG: # debug flag
            print(f"Result: {result}")

        if result[0] == False: # invalid auth
            #TODO: prettify
            printc("INVALID AUTHORIZATION")
            printc("ACCESS DENIED")
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
                    send(server, "CREATE SCP")  # send create request to server
                    response = recv(server)

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

                    send(server, scp) # send scp data to server
                elif split_request[1] == "MTF":
                    # TODO
                    print("NOT YET IMPLEMENTED")
                elif split_request[1] == "SITE":
                    # TODO
                    print("NOT YET IMPLEMENTED")
                elif split_request[1] == "USER":
                    # TODO
                    print("NOT YET IMPLEMENTED") 
                elif split_request[1] == "SITE":
                    # TODO
                    print("NOT YET IMPLEMENTED")
                else:
                    # TODO: Better message
                    printc(f"INVALID: {split_request[1]!r}")

            elif split_request[0] == "ACCESS": # usr wants to access a file
                if split_request[1] == "SCP":  # scp file
                    print(f"Requesting access to file SCP-{split_request[2]}. . .")
                    send(server, f"ACCESS SCP {split_request[2]}")
                    response = recv(server)

                    if not response: # no data, some error happened
                        printc("[ERROR]: NO RESPONSE FROM DEEPWELL")
                        server.close()
                        sys.exit()
                    
                    # decode
                    response = decode(response)
                    if response["status"] == "EXPUNGED":
                        art.expunged(split_request[2])
                    elif response["status"] == "REDACTED":
                        art.redacted(split_request[2], response["f_classification"], response["usr_clearance"])
                    elif response["status"] == "GRANTED":
                        art.granted(split_request[2])
                        display_scp(response, console)
                    else:
                        printc("[ERROR]")
                        printc("INVALID RESPONSE FROM SERVER")
                elif split_request[1] == "MTF":
                    # TODO
                    print("NOT YET IMPLEMENTED")
                elif split_request[1] == "SITE":
                    # TODO
                    print("NOT YET IMPLEMENTED")
                elif split_request[1] == "USER":
                    # TODO
                    print("NOT YET IMPLEMENTED") 
                elif split_request[1] == "SITE":
                    # TODO
                    print("NOT YET IMPLEMENTED")
                else:
                    # TODO: Better message
                    printc(f"INVALID: {split_request[1]!r}")
            else:
                print("INVALID COMMAND")