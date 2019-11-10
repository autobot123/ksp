from pdb import set_trace as breakpoint
from krpc_FUNCTIONS import Launcher

test = Launcher(sas_activated=True, launch_num_stages=1, script_name="KerbSat Launch")
test.launch()
test.gravity_turn()

test.circularise()

#todo distinguish between SRBs and LF engines for grav turn. split out somehow.