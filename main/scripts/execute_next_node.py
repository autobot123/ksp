from functions.orbit import Orbit


def request_user_input(msg, proceed_string="yes", abort_string="no"):

    query_response = input(f"\n{msg}"
                           f"\nEnter {proceed_string} to execute node"
                           f"\nEnter {abort_string} to abort script\n\n")
    while True:
        if query_response == proceed_string:
            print("Proceeding")
            return
        elif query_response == abort_string:
            print("Aborting")
            exit()
        else:
            query_response = input(f"Invalid input. Please enter {proceed_string} or {abort_string}\n")
            continue

orbit = Orbit()
proceed_string = "yes"

while proceed_string == "yes":

    request_user_input("Running execute node loop.")
    print("  Running execute node script")
    orbit.execute_next_node()
    print("Exiting execute node script")

print("Stopping script")
