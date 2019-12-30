from functions.orbit import Orbit


print("Running transfer script")
orbit = Orbit()

# setup resonant dive orbit for 3 satellite coverage of Kerbin
orbit.set_apo(750000)
orbit.set_peri(110485.6)

# # circularise satellites
# orbit.circularise_to_apoapsis()

print("Exiting transfer script")