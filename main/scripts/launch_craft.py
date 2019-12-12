# import sys
# sys.path.insert(1, "functions")

from functions.launcher import Launcher


print("Running launcher script")
launcher = Launcher()

launcher.launch()
launcher.gravity_turn()
launcher.circularise()
print("Exiting launcher script")
