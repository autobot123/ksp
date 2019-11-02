import krpc
import time
import math
import json
import os


json_config = os.path.join(os.getcwd(), r"C:\projects\ksp\main\resources\craft_config\suborbitalflight_config.json")

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

stage_resources = vessel.parts.in_stage(vessel.control.current_stage)

while 500 < altitude() < 5000:
    for part in stage_resources:
        if "solid" in part.name:
            solid_fuel = part.resources.amount(name="SolidFuel")
            print("solid fuel: {}".format(solid_fuel))
        if "engine" in part.name:
            liquid_fuel = part.resources.amount(name="LiquidFuel")
            print("liquid fuel: {}".format(liquid_fuel))
