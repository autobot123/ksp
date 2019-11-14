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

with open(json_config, "r") as json_file:
    flight_params = json.load(json_file)


### testbed

def execute_next_node():
    
    nodes = vessel.control.nodes
    next_node = nodes[0]
    delta_v = next_node.delta_v
    print(f"node delta V: {delta_v}")
    
    vessel.auto_pilot.engage()
    vessel.auto_pilot.reference_frame = next_node.reference_frame
    vessel.auto_pilot.target_direction = (0, 1, 0)
    vessel.auto_pilot.wait()

    F = vessel.available_thrust
    Isp = vessel.specific_impulse * 9.82
    m0 = vessel.mass
    m1 = m0 / math.exp(delta_v / Isp)
    flow_rate = F / Isp
    burn_time = (m0 - m1) / flow_rate

    print("Burn time: ", burn_time)

    burn_ut = next_node.ut
    print(f'Warp to {burn_ut} second to burn')
    lead_time = 5
    conn.space_center.warp_to(burn_ut - lead_time - burn_time)

    print('Ready to execute burn')
    burn_dv = conn.add_stream(getattr, next_node, "remaining_delta_v")

    while (burn_ut - ut()) - (burn_time/2) > 0:
        countdown_to_burn = (burn_ut - ut()) - (burn_time/2)
        print(f"countdown to burn: {round(countdown_to_burn,2)}")
        time.sleep(0.1)
        pass

    print(f'Burning for {round(burn_time,2)} seconds')
    vessel.control.throttle = 1.0

    new_burn_dv = 10000000
    decimal.getcontext().prec = 3
    while True:
        # multiply by 1 to ensure values are rounded as per precision above
        old_burn_dv = decimal.Decimal(new_burn_dv) * 1
        new_burn_dv = decimal.Decimal(burn_dv()) * 1
        #print(f"old_burn_dv: {old_burn_dv}, new_burn_dv: {new_burn_dv}\n{new_burn_dv > old_burn_dv}")
        #time.sleep(0.1)
        if 5 < new_burn_dv < 20:
            vessel.control.throttle = 0.5
        elif 1 < new_burn_dv < 5:
            vessel.control.throttle = 0.1
        elif burn_dv() < 1:
            vessel.control.throttle = 0.01
        if new_burn_dv < 0.01:
            vessel.control.throttle = 0.0
            print(f"final delta v remaining: {new_burn_dv}m/s")
            break
        elif new_burn_dv > old_burn_dv:
            vessel.control.throttle = 0.0
            break

    vessel.auto_pilot.disengage()
    next_node.remove()
    vessel.control.sas = True
    print('Launch complete')
    


execute_next_node()



### /testbed
