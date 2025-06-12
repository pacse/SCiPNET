from CS50xFP.old.utils import clear, login, register_user, verify_override_phrase, log_event, load_credentials, process_command
import time

logged_in = False

# Main loop
while True:
    if not logged_in:
        # Clear the screen
        clear()

        # Welcome message
        print("Welcome to the SCiPNET Access Terminal!\n")
        print("The foundation database is classified.\nUnauthorized access will result in detainment.\nPlease login or register. Enter quit to shutdown the terminal.")

        # Login loop
        while True:
            imp = input(">>> ").lower()
            if imp == "login" or "register":
                break

            elif imp == "quit":
                print("Shutting Down...")
                time.sleep(1)
                quit()

        if imp == "login":
            while True:
                name = input("Name: ")
                password = input("Password: ")


                is_verified, user_id = login(name, password)
                if is_verified:
                    logged_in = True
                    break

        elif imp == "register":
            while True:
                print("Please enter override phrase (clearance 3 or higher)")
                is_verified, authorizer, auth_clearance = verify_override_phrase(input(">>> "), 3)

                if is_verified:
                    print("Override phrase accepted\n\nWelcome new foundation employee!")
                    break

                else:
                    print("Override phrase denied\n")

            # Register the new user returning their new ID
            user_id = register_user(authorizer, auth_clearance)


    # User has logged in/has been registered
    else:
        log_event(user_id, f"User logged in")
        # Load user details
        user = load_credentials(user_id)

        title = user["title"]
        clearance = user["clearance"]
        site = user["site"]

        clear()
        print(f"User authenticated\nWelcome {title} {name}! (clearance level: {clearance})")
        print("Enter help for help")
        while True:
            imp = input(">>> ").lower().split()

            logged_in = process_command(imp, clearance)
            if not logged_in:
                break
