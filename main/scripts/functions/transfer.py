from .core import Core
import math
import time


class Transfer(Core):

    def __init__(self):

        super().__init__()

    # todo
    def capture_circularise(self):

        self.vessel.auto_pilot.engage()
        mu = self.vessel.orbit.body.gravitational_parameter
        # fixme - change to periapsis?
        r = self.vessel.orbit.apoapsis
        # fixme - change to semi minor axis?
        a1 = self.vessel.orbit.semi_major_axis
        a2 = r
        v1 = math.sqrt(mu * ((2. / r) - (1. / a1)))
        v2 = math.sqrt(mu * ((2. / r) - (1. / a2)))
        delta_v = v2 - v1
        # fixme change to time to periapsis? and retrograde = delta_v?
        node = self.vessel.control.add_node(self.ut() + self.vessel.orbit.time_to_apoapsis, prograde=delta_v)

        self.execute_next_node()

        print('Launch complete')
        time.sleep(1)
        self.sas_prograde()
