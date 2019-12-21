import time
import asyncio
import math
from .core import Core


class AsyncLauncher(Core):

    def __init__(self, target_apo=100000, target_peri=100000):

        super().__init__()
        self.launch_complete = False
        self.target_apo = target_apo
        self.target_peri = target_peri
        print("Launch parameters: Target apo = {}    Target peri = {}".format(self.target_apo, self.target_peri))

        self.alt_turn_start = self.launch_params['alt_turn_start']
        self.alt_turn_end = self.launch_params['alt_turn_end']
        self.final_pitch = self.launch_params['final_pitch']
        self.warp = self.launch_params['warp']
        self.srbs_separated = self.launch_params['srbs_separated']
        self.lf_launch_stage_expended = self.launch_params['lf_launch_stage_expended']

        print('Launch parameters: {}'.format(self.launch_params))

    def launch(self, launch_num_stages=1, sas_activated=True, warp=0):
        self.set_phys_warp(warp)
        print("Launching vessel")
        self.vessel.control.throttle = 1
        for i in range(launch_num_stages):
            self.vessel.control.activate_next_stage()
        self.vessel.control.sas = sas_activated
        time.sleep(0.1)
        print("Liftoff")

    async def gravity_turn(self):

        compass_heading = 90
        turn_angle = 0
        self.vessel.auto_pilot.engage()
        self.vessel.auto_pilot.target_pitch_and_heading(90, compass_heading)
        while self.altitude() < 0.9*self.alt_turn_start:
            pass
        self.set_phys_warp(self.warp)
        print("Commence turn")

        while not self.launch_complete:
            if self.alt_turn_start < self.altitude() < self.alt_turn_end:
                frac = ((self.altitude() - self.alt_turn_start) / (self.alt_turn_end - self.alt_turn_start))
                new_turn_angle = frac * 90
                if abs(new_turn_angle - turn_angle) > 0.5:
                    turn_angle = 90-new_turn_angle + frac*self.final_pitch
                    self.vessel.auto_pilot.target_pitch_and_heading(turn_angle, compass_heading)
            if self.apoapsis() > self.target_apo:
                self.launch_complete = True
            await asyncio.sleep(0.1)

        print("Gravity turn complete. Coasting to apoapsis")
        self.sas_prograde()
        self.vessel.control.throttle = 0

    async def async_stage_when_engine_empty(self):

        while not self.launch_complete:
            active_stage = self.vessel.control.current_stage
            part_names = [part.title for part in self.vessel.parts.in_stage(active_stage)]

            print(f"Active stage: {active_stage}    Parts in active stage: {part_names}")

            engines = self.get_active_engines()
            staged = False
            while not staged:
                for engine in engines:
                    if not engine.has_fuel:
                        staged = True
                await asyncio.sleep(0.01)

            self.activate_stage()

    def circularise(self):

        while self.altitude() < 70000:
            pass

        ## todo create core method
        self.vessel.auto_pilot.engage()
        mu = self.vessel.orbit.body.gravitational_parameter
        r = self.vessel.orbit.apoapsis
        a1 = self.vessel.orbit.semi_major_axis
        a2 = r
        v1 = math.sqrt(mu * ((2. / r) - (1. / a1)))
        v2 = math.sqrt(mu * ((2. / r) - (1. / a2)))
        delta_v = v2 - v1
        node = self.vessel.control.add_node(self.ut() + self.vessel.orbit.time_to_apoapsis, prograde=delta_v)

        self.execute_next_node()

        print('Launch complete')
        time.sleep(1)
        self.sas_prograde()
