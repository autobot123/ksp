from .core import Core
import math
import time


# fixme redundant? just use orbit.py
class Transfer(Core):

    def __init__(self):

        super().__init__()

    # todo
    def circularise_to_periapsis(self):

        self.vessel.auto_pilot.engage()
        mu = self.vessel.orbit.body.gravitational_parameter
        r = self.vessel.orbit.periapsis
        a1 = self.vessel.orbit.semi_minor_axis
        a2 = r
        v1 = math.sqrt(mu * ((2. / r) - (1. / a1)))
        v2 = math.sqrt(mu * ((2. / r) - (1. / a2)))
        delta_v = v2 - v1
        node = self.vessel.control.add_node(self.ut() + self.vessel.orbit.time_to_periapsis, prograde=delta_v)

        self.execute_next_node()

        print('Launch complete')
        time.sleep(1)
        self.sas_prograde()
