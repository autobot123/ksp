import krpc
import time
import math
import json
import os


json_config = os.path.join(os.getcwd(), r"..\resources\moonsat1_config.json")

conn = krpc.connect(name="debugging_script")
canvas = conn.ui.stock_canvas
vessel = conn.space_center.active_vessel
srf_frame = vessel.orbit.body.reference_frame

ut = conn.add_stream(getattr, conn.space_center, 'ut')
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
periapsis = conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude')

with open(json_config, "r") as json_file:
    flight_params = json.load(json_file)