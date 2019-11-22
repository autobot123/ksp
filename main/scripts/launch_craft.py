import sys
sys.path.insert(1, "functions")

from core import Core
from lander import Lander
from launcher import Launcher
from orbit import Orbit
from transfer import Transfer


print("Running launcher script")
launcher = Launcher()

launcher.launch()
launcher.gravity_turn()
launcher.circularise()
print("Exiting launcher script")
