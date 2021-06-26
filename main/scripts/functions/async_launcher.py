import time
import asyncio
import math
from .core import Core


class AsyncLauncher(Core):

    def __init__(self, target_apo=80000, target_peri=80000, compass_heading=90):

        super().__init__()
        self.gravity_turn_active = False
        self.target_apo_reached = False
        self.circularisation_active = False
        self.circularisation_complete = False
        self.target_apo = target_apo
        self.target_peri = target_peri
        print("Launch parameters: Target apo = {}    Target peri = {}".format(self.target_apo, self.target_peri))

        self.alt_turn_start = self.launch_params['alt_turn_start']
        self.alt_turn_end = self.launch_params['alt_turn_end']
        self.final_pitch = self.launch_params['final_pitch']
        self.warp = self.launch_params['warp']
        self.srbs_separated = self.launch_params['srbs_separated']
        self.lf_launch_stage_expended = self.launch_params['lf_launch_stage_expended']

        self.compass_heading = compass_heading
        self.turn_angle = 0

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

        self.vessel.auto_pilot.engage()
        self.vessel.auto_pilot.target_pitch_and_heading(90, self.compass_heading)

        while not self.gravity_turn_active:
            await asyncio.sleep(0.1)

        print(f"Commencing turn at {self.altitude():.0f} metres")
        while not self.target_apo_reached:
            frac = ((self.altitude() - self.alt_turn_start) / (self.alt_turn_end - self.alt_turn_start))
            new_turn_angle = frac * 90
            if abs(new_turn_angle - self.turn_angle) > 1:
                self.turn_angle = 90-new_turn_angle + frac*self.final_pitch
                if self.turn_angle < self.final_pitch:
                    self.turn_angle = self.final_pitch
                self.vessel.auto_pilot.target_pitch_and_heading(self.turn_angle, self.compass_heading)
                # logger.debug(f"turn angle: {turn_angle:.0f}, compass heading: {compass_heading}")
            await asyncio.sleep(0.1)

        print(f"Gravity turn complete.")

    async def async_stage_when_engine_empty(self):

        while not self.circularisation_complete:
            engines = self.get_active_engines()
            staged = False
            while not staged:
                if self.circularisation_complete:
                    staged = True
                for engine in engines:
                    if not engine.has_fuel:
                        staged = True
                await asyncio.sleep(0.01)

            if not self.circularisation_complete:
                self.activate_stage("Staging")

        print("Auto staging complete")

    async def circularise(self):

        while not self.circularisation_active:
            await asyncio.sleep(0.5)
        print("Commencing circularisation")

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
        self.circularisation_complete = True


    # todo try using async main loop in monitor launch state instead of separate launch script?
    async def monitor_launch_state(self):

        while not self.gravity_turn_active:
            if self.alt_turn_start < self.altitude() < self.alt_turn_end:
                self.gravity_turn_active = True
                print(f"Gravity turn active = {self.gravity_turn_active}")
            await asyncio.sleep(0.1)

        while self.gravity_turn_active:
            if self.altitude() > self.alt_turn_end:
                self.gravity_turn_active = False
                print(f"Gravity turn active = {self.gravity_turn_active}")
            await asyncio.sleep(0.1)

        while not self.target_apo_reached:
            if self.apoapsis() > self.target_apo:
                self.target_apo_reached = True
                print(f"Target apo reached = {self.target_apo_reached}")
            await asyncio.sleep(0.1)

        self.vessel.control.throttle = 0
        self.sas_prograde()

        self.set_phys_warp(3)

        while not self.circularisation_active:
            while self.vessel.orbit.body.pressure_at(self.altitude()) != 0:
                # print(f"pressure: {self.vessel.orbit.body.pressure_at(self.altitude()):.1f}")
                await asyncio.sleep(0.5)
            self.circularisation_active = True
            self.set_phys_warp(0)

        while not self.circularisation_complete:
            await asyncio.sleep(0.1)

        print("Launch complete. Craft inactive.")
        time.sleep(1)
        self.sas_prograde()
