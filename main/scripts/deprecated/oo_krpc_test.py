from pdb import set_trace as breakpoint
from krpc_FUNCTIONS import Core, Launcher, Orbit

test = Launcher(script_name="test")
test.launch(warp=0)
test.gravity_turn(warp=0)
test.circularise()

# # test.launch_it()
# test.grav_turn(8000)
# test.separate_booster(num_stages=2, stage_desc="main engine", fuel_cutoff=0.1)
# test.sas_prograde()

# create info display class for info_display and call functions from this script
# wait for apoapsis
# circularise
# stop at periapsis
# print orbital details
# add panels