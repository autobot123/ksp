import krpc
import time
import math
import json
import os
from pdb import set_trace as bp
import decimal

print(os.getcwd())

json_config = os.path.join(os.getcwd(), r"C:\projects\ksp\main\resources\craft_config\suborbitalflight_config.json")

conn = krpc.connect(name="debugging_script")
canvas = conn.ui.stock_canvas
vessel = conn.space_center.active_vessel
srf_frame = vessel.orbit.body.reference_frame

ut = conn.add_stream(getattr, conn.space_center, 'ut')
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
periapsis = conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude')

#with open(json_config, "r") as json_file:
#    flight_params = json.load(json_file)


### testbed

def enable_sas():

    try:
        vessel.auto_pilot.disengage()
        vessel.control.sas = True
        time.sleep(0.1)
        return True

    except RuntimeError:
        print("Cannot set SAS mode of vessel")
        return False

def sas_prograde():

    enable_sas()
    try:
        vessel.control.sas_mode = vessel.control.sas_mode.prograde
    except RuntimeError:
        print("Error: Cannot set SAS mode of vessel to prograde")

### /testbed
        
