import sys
sys.path.insert(1, "functions")

from core import Core
from lander import Lander
from launcher import Launcher
from orbit import Orbit
from transfer import Transfer


print("Running execute node script")
core = Core()

core.execute_next_node()
print("Exiting execute node script")
