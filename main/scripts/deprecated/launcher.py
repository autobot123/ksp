import time
import math
from functions.core import Core


class Launcher(Core):

    def __init__(self, target_apo=100000, target_peri=100000):

        super().__init__()
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

    def gravity_turn(self):

        compass_heading = 90
        turn_angle = 0

        self.vessel.auto_pilot.engage()
        self.vessel.auto_pilot.target_pitch_and_heading(90, compass_heading)

        while self.altitude() < 0.9*self.alt_turn_start:
            pass

        self.set_phys_warp(self.warp)

        print("Entering gravity turn loop")

        engines = self.get_active_engines()

        while True:

            if self.altitude() > self.alt_turn_start and self.altitude() < self.alt_turn_end:
                frac = ((self.altitude() - self.alt_turn_start) / (self.alt_turn_end - self.alt_turn_start))
                new_turn_angle = frac * 90
                if abs(new_turn_angle - turn_angle) > 0.5:
                    turn_angle = 90-new_turn_angle + frac*self.final_pitch
                    self.vessel.auto_pilot.target_pitch_and_heading(turn_angle, compass_heading)

            engine_staged = False
            if engines:
                for engine in engines:
                    if not engine.has_fuel:
                        print(f"{engine.part.title} fuel expended. Staging")
                        engine_staged = True
                if engine_staged:
                    self.activate_stage()
                    engines = self.get_active_engines()

            if self.apoapsis() > self.target_apo:
                break

            time.sleep(0.1)

        print("Gravity turn complete. Coasting to apoapsis")
        self.sas_prograde()
        self.vessel.control.throttle = 0

    def circularise(self):

        while self.altitude() < 70000:
            pass

        ## TODO: create core method
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

    def deprecated_circularise_code(self):
        """
        replaced by calling self.execute_next_node()
        :return:
        """


        ## TODO: create core method
        F = self.vessel.available_thrust
        Isp = self.vessel.specific_impulse * 9.82
        m0 = self.vessel.mass
        m1 = m0 / math.exp(delta_v / Isp)
        flow_rate = F / Isp
        burn_time = (m0 - m1) / flow_rate

        print("Burn time: ", burn_time)

        # Orientate ship
        print('Orientating ship for circularization burn')
        self.vessel.auto_pilot.reference_frame = node.reference_frame
        self.vessel.auto_pilot.target_direction = (0, 1, 0)
        self.vessel.auto_pilot.wait()

        # Wait until burn
        print('Waiting until circularization burn')
        burn_ut = self.ut() + self.vessel.orbit.time_to_apoapsis - (burn_time / 2.)
        lead_time = 5
        self.conn.space_center.warp_to(burn_ut - lead_time)

        # Execute burn
        print('Ready to execute burn')
        time_to_apoapsis = self.conn.add_stream(getattr, self.vessel.orbit, 'time_to_apoapsis')
        while time_to_apoapsis() - (burn_time / 2.) > 0:
            pass
        print('Executing burn')
        self.vessel.control.throttle = 1.0

        # fixme overshoots burns when launching into orbit. use remaing_burn earlier?
        time.sleep(burn_time - 0.1)
        print('Fine tuning')
        self.vessel.control.throttle = 0.05
        remaining_burn =self.conn.add_stream(node.remaining_burn_vector, node.reference_frame)

        ## preferred method of ending burn
        while remaining_burn()[1] > 0.1:
            print(remaining_burn()[1])
            pass
        self.vessel.control.throttle = 0.0
        node.remove()