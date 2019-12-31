import sys
sys.path.append("..")
import asyncio
import time
from scripts.functions.async_launcher import AsyncLauncher
from scripts.functions.orbit import Orbit


def request_user_input(msg, proceed_string="YES", abort_string="NO"):

    query_response = input(f"\n{msg}"
                           f"\nEnter {proceed_string} to proceed"
                           f"\nEnter {abort_string} to abort\n")
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


print("Loading mission plan to launch satellites around Mun and Minmus")

# todo test and uncomment
# # launch craft
# launcher = AsyncLauncher()
# print("Running async launcher script")
# launcher.launch(warp=0)
#
# await asyncio.gather(launcher.monitor_launch_state(),
#                      launcher.async_stage_when_engine_empty(),
#                      launcher.gravity_turn(),
#                      launcher.circularise())
#
# print("Exiting async launcher script")

orbit = Orbit()

# plan Minmus encounter

# todo uncomment
# request_user_input(f"Create maneuver node to encounter Minmus.")
# orbit.execute_next_node()

# setup Satellite A in Minmus orbit
request_user_input(f"Separate satellite A, activate engine and solar panels and switch. Create maneuver node to set peri at Minmus.")
satA = Orbit()
satA.execute_next_node()

request_user_input("Create maneuver node to set apo at Minmus.")
satA.execute_next_node()

# plan Mun encounter
request_user_input(f"Switch to main craft and setup node to encounter Mun.")
main_craft = Orbit()
main_craft.execute_next_node()

# setup Satellite B in Mun orbit
request_user_input(f"Separate satellite B, activate engine and solar panels and switch. Create maneuver node to set peri at Mun.")
satB = Orbit()
satB.execute_next_node()

# return home
request_user_input(f"Switch to parent craft and create node to return home.")
main_craft.execute_next_node()

request_user_input("Create maneuver node to set apo at Mun.")
satB.execute_next_node()

print("Mission complete")





# async def launch():
#
#     print("Running async launcher script")
#     launcher = AsyncLauncher()
#     launcher.launch(warp=0)
#
#     await asyncio.gather(launcher.monitor_launch_state(),
#                          launcher.async_stage_when_engine_empty(),
#                          launcher.gravity_turn(),
#                          launcher.circularise())
#
#     print("Exiting async launcher script")
#
#
# if __name__ == "__main__":
#     asyncio.run(launch())
