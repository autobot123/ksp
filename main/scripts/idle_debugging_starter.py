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
surface_altitude = conn.add_stream(getattr, vessel.flight(), 'surface_altitude')



#with open(json_config, "r") as json_file:
#    flight_params = json.load(json_file)

def get_atts(item):
    
    for i in dir(item):
             print(i, getattr(item, i))

#get_atts(srb)


### testbed

while True:
    
    print(f"air pressure = {vessel.orbit.body.pressure_at(altitude())}")
    time.sleep(0.5)

### /testbed
