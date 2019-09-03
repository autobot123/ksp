import krpc
import time
import math

# todo add target apo and peri to class

"""
cmd line:
from krpc_FUNCTIONS import Core, Launcher, Orbit
"""


class Core:

    def __init__(self, script_name="kRPC script"):
        # connections
        self.conn = krpc.connect(name=script_name)
        self.canvas = self.conn.ui.stock_canvas
        self.vessel = self.conn.space_center.active_vessel
        self.srf_frame = self.vessel.orbit.body.reference_frame

        # flight info
        self.ut = self.conn.add_stream(getattr, self.conn.space_center, 'ut')
        self.altitude = self.conn.add_stream(getattr, self.vessel.flight(), 'mean_altitude')
        self.apoapsis = self.conn.add_stream(getattr, self.vessel.orbit, 'apoapsis_altitude')
        self.periapsis = self.conn.add_stream(getattr, self.vessel.orbit, 'periapsis_altitude')
        self.stage_1_resources = self.vessel.resources_in_decouple_stage(stage=1, cumulative=False)
        self.srb_fuel = self.conn.add_stream(self.stage_1_resources.amount, 'SolidFuel')

    def sas_prograde(self):
        ## todo: one method for sas? pass in sas_mode as arg
        self.vessel.auto_pilot.disengage()
        self.vessel.control.sas = True
        time.sleep(0.1)
        self.vessel.control.sas_mode = self.vessel.control.sas_mode.prograde

    def sas_retrograde(self):
        self.vessel.auto_pilot.disengage()
        self.vessel.control.sas = True
        time.sleep(0.1)
        self.vessel.control.sas_mode = self.vessel.control.sas_mode.retrograde

    def sas_target(self):
        self.vessel.auto_pilot.disengage()
        self.vessel.control.sas = True
        time.sleep(0.1)
        self.vessel.control.sas_mode = self.vessel.control.sas_mode.target

    def set_pitch_heading(self, pitch, heading):
        self.auto_pilot.engage()
        time.sleep(0.1)
        self.vessel.auto_pilot.target_pitch_and_heading(pitch, heading)

    def activate_stage(self):
        self.vessel.control.activate_next_stage()

    def set_phys_warp(self, factor=0):
        print("setting warp to ", factor)
        self.conn.space_center.physics_warp_factor = factor

    ## todo test
    def get_fuel_quantity(self):
        solid_fuel = self.conn.get_call(self.vessel.resources.amount, "SolidFuel")
        liquid_fuel = self.conn.get_call(self.vessel.resources.amount, "LiquidFuel")
        return solid_fuel, liquid_fuel


    def warp_to(self, time):
        ## fixme below command unreliable
        self.conn.space_center.warp_to(time)
        ## todo use set_apo time warp in this method? work out how to scale warping

class Launcher(Core):

    def __init__(self, script_name='kRPC script', target_apo=100000, target_peri=100000):
        super().__init__(script_name=script_name)
        self.target_apo = target_apo
        self.target_peri = target_peri
        print("Launch parameters: Target apo = {}    Target peri = {}"
        .format(self.target_apo, self.target_peri))

    def launch(self, launch_num_stages=1, sas_activated=True, warp=0):
        self.set_phys_warp(warp)
        print("Launching vessel")
        self.vessel.control.throttle = 1
        for i in range(launch_num_stages):
            self.vessel.control.activate_next_stage()
        self.vessel.control.sas = sas_activated
        time.sleep(0.1)

    def gravity_turn(self, alt_turn_start=3000, alt_turn_end=20000, final_pitch=25, warp=0):

        srbs_separated = False
        turn_angle = 0

        self.vessel.auto_pilot.engage()
        self.vessel.auto_pilot.target_pitch_and_heading(90, 90)

        while self.altitude() < 0.9*alt_turn_start:
            pass

        self.set_phys_warp(warp)

        while True:

            if self.altitude() > alt_turn_start and self.altitude() < alt_turn_end:
                frac = ((self.altitude() - alt_turn_start) / (alt_turn_end - alt_turn_start))
                new_turn_angle = frac * 90
                if abs(new_turn_angle - turn_angle) > 0.5:
                    turn_angle = 90-new_turn_angle + frac*final_pitch
                    self.vessel.auto_pilot.target_pitch_and_heading(turn_angle, 90)

            if not srbs_separated:
                if self.srb_fuel() < 0.1:
                    print("SRBs done")
                    self.vessel.control.activate_next_stage()
                    self.vessel.control.activate_next_stage()
                    srbs_separated = True

            if self.apoapsis() > self.target_apo:
                break

            time.sleep(0.1)

        print("Gravity turn finished, coasting to apoapsis")
        self.sas_prograde()
        self.vessel.control.throttle = 0


    def gravity_turn_no_staging(self, alt_turn_start=3000, alt_turn_end=20000, final_pitch=25, warp=0):

        ##todo improve turn logic. get it smoother. what to do with final pithc and where to point?

        turn_angle = 0

        self.vessel.auto_pilot.engage()
        self.vessel.auto_pilot.target_pitch_and_heading(90, 90)

        while self.altitude() < 0.9*alt_turn_start:
            pass

        self.set_phys_warp(warp)

        while True:

            if self.altitude() > alt_turn_start and self.altitude() < alt_turn_end:
                frac = ((self.altitude() - alt_turn_start) / (alt_turn_end - alt_turn_start))
                new_turn_angle = frac * 90
                if abs(new_turn_angle - turn_angle) > 0.5:
                    turn_angle = 90-new_turn_angle + frac*final_pitch
                    self.vessel.auto_pilot.target_pitch_and_heading(turn_angle, 90)

            if self.apoapsis() > self.target_apo:
                break

            time.sleep(0.1)

        print("Gravity turn finished, coasting to apoapsis")
        self.sas_prograde()
        self.vessel.control.throttle = 0


    def circularise(self):

        while self.altitude() < 70000:
            pass

        ## todo create core method
        mu = self.vessel.orbit.body.gravitational_parameter
        r = self.vessel.orbit.apoapsis
        a1 = self.vessel.orbit.semi_major_axis
        a2 = r
        v1 = math.sqrt(mu * ((2. / r) - (1. / a1)))
        v2 = math.sqrt(mu * ((2. / r) - (1. / a2)))
        delta_v = v2 - v1
        node = self.vessel.control.add_node(self.ut() + self.vessel.orbit.time_to_apoapsis, prograde=delta_v)

        ## todo create core method
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
        time.sleep(burn_time - 0.1)
        print('Fine tuning')
        self.vessel.control.throttle = 0.05
        remaining_burn =self.conn.add_stream(node.remaining_burn_vector, node.reference_frame)
        # while remaining_burn()[1] > 0:
        while self.periapsis() < 0.99*self.target_peri:
            pass
        self.vessel.control.throttle = 0.0
        node.remove()

        print('Launch complete')


class Orbit(Core):

    def set_apo(self, apo_target, wait_til_peri=True, burn_time=30, turn_time=5):

        if wait_til_peri:
            while self.vessel.orbit.time_to_periapsis > burn_time*3:
                self.conn.space_center.rails_warp_factor = 3
            while self.vessel.orbit.time_to_periapsis > burn_time:
                self.conn.space_center.rails_warp_factor = 2

        self.conn.space_center.rails_warp_factor = 0

        print("Orienting craft")
        if self.apoapsis() < apo_target:
            self.sas_prograde()
        elif self.apoapsis() > apo_target:
            self.sas_retrograde()

        time.sleep(turn_time)

        print("Performing burn")
        while self.apoapsis() < 0.95* apo_target:
            self.vessel.control.throttle = 1
        while self.apoapsis() < 0.99* apo_target:
            self.vessel.control.throttle = 0.1
        while self.apoapsis() < 0.99999* apo_target:
            self.vessel.control.throttle = 0.01

        self.vessel.control.throttle = 0
        apo_actual = self.apoapsis()
        print("Burn complete. Target apo: {}  Actual apo: {}".format(apo_target, apo_actual))


    def set_peri(self, peri_target, wait_til_apo=True, burn_time=30, turn_time=5):
        ## todo check if burn should be prograde or retrograde

        if wait_til_apo:
            while self.vessel.orbit.time_to_apoapsis > burn_time*3:
                self.conn.space_center.rails_warp_factor = 3
            while self.vessel.orbit.time_to_apoapsis > burn_time:
                self.conn.space_center.rails_warp_factor = 2

        self.conn.space_center.rails_warp_factor = 0

        print("Orienting craft")
        if self.periapsis() < peri_target:
            self.sas_prograde()
        elif self.periapsis() > peri_target:
            self.sas_retrograde()

        time.sleep(turn_time)

        print("Performing burn")
        while self.periapsis() < 0.95* peri_target:
            self.vessel.control.throttle = 1
        while self.periapsis() < 0.99* peri_target:
            self.vessel.control.throttle = 0.1
        while self.periapsis() < 0.99999* peri_target:
            self.vessel.control.throttle = 0.01

        self.vessel.control.throttle = 0
        peri_actual = self.periapsis()
        print("Burn complete. Target peri: {}  Actual peri: {}".format(peri_target, peri_actual))

    def circularise_to_apo(self):

        self.vessel.auto_pilot.engage()

        mu = self.vessel.orbit.body.gravitational_parameter
        r = self.vessel.orbit.apoapsis
        a1 = self.vessel.orbit.semi_major_axis
        a2 = r
        v1 = math.sqrt(mu * ((2. / r) - (1. / a1)))
        v2 = math.sqrt(mu * ((2. / r) - (1. / a2)))
        delta_v = v2 - v1
        node = self.vessel.control.add_node(self.ut() + self.vessel.orbit.time_to_apoapsis, prograde=delta_v)

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
        time.sleep(burn_time - 0.1)
        print('Fine tuning')
        self.vessel.control.throttle = 0.05
        breakpoint()
        remaining_burn = self.conn.add_stream(node.remaining_burn_vector, node.reference_frame)

        #fixme use node.remaining_delta_v instead? "dumb" method, would have to use some low value like <0.2
        while remaining_burn()[1] > 0:
            print("\nRemaining burn vector item 2: {}".format(remaining_burn()[1]))
            print("Remaining delta v: {}\n".format(node.remaining_delta_v))
            time.sleep(1)

            pass
        self.vessel.control.throttle = 0.0
        node.remove()


def main():

    launcher = Launcher()
    orbit = Orbit()

    launcher.launch()
    launcher.gravity_turn_no_staging()
    launcher.circularise()


if __name__ == "__main__":

    main()
