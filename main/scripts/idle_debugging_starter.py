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


### testbed

direction_dict = {"prograde": "normal",
                  "retrograde": "anti-normal",
                  "normal": "prograde",
                  "anti_normal": "retrograde",
                  "radial": "radial",
                  "anti_radial": "anti-radial"}

ref_frame = vessel.orbital_reference_frame

def set_orientation(direction):

    direction = direction.lower()
    direction_dict = {"prograde": "normal",
                      "retrograde": "anti-normal",
                      "normal": "prograde",
                      "anti_normal": "retrograde",
                      "radial": "radial",
                      "anti_radial": "anti-radial"}
    if direction not in direction_dict.keys():
        print("Please enter a valid direction")
        raise Exception(f"Invalid direction specified: {direction}")

    # adjust direction (pro/retrograde actually point normal/anti-normal and vice versa)
    direction = direction_dict[direction]

    # check SAS disabled and auto pilot enabled
    if vessel.control.sas:
        vessel.control.sas = False
    vessel.auto_pilot.engage()

    # set direction
    ref_frame = vessel.orbital_reference_frame
    direction = conn.add_stream(getattr, vessel.flight(ref_frame), direction)
    vessel.auto_pilot.target_direction = direction()

    # wait for vessel to lineup
    vessel.auto_pilot.wait()
    print(f"Vessel oriented to {direction}")


### /testbed


#exit()


stage_resources = vessel.parts.in_stage(vessel.control.current_stage)

while 500 < altitude() < 5000:
    for part in stage_resources:
        if "solid" in part.name:
            solid_fuel = part.resources.amount(name="SolidFuel")
            print("solid fuel: {}".format(solid_fuel))
        if "engine" in part.name:
            liquid_fuel = part.resources.amount(name="LiquidFuel")
            print("liquid fuel: {}".format(liquid_fuel))


node = vessel.control.nodes
for i in node:
	 i.orbit.body.name
