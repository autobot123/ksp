import krpc
import time
import math
import json
import os

# todo add target apo and peri to class

"""
cmd line:
from krpc_FUNCTIONS import Core, Launcher, Orbit
"""


class Core:

    def __init__(self):
        """
        :param json_config: full path to json config file for ship
        """

        json_config = self.select_craft_config()

        with open(json_config, "r") as json_file:
            craft_params = json.load(json_file)

        self.craft_params = craft_params
        self.launch_params = self.craft_params['launch_params']

        # connections
        # self.json_config = json_config
        self.conn = krpc.connect(name=craft_params['script_name'])
        self.canvas = self.conn.ui.stock_canvas
        self.vessel = self.conn.space_center.active_vessel
        self.srf_frame = self.vessel.orbit.body.reference_frame

        # flight info
        self.ut = self.conn.add_stream(getattr, self.conn.space_center, 'ut')
        self.altitude = self.conn.add_stream(getattr, self.vessel.flight(), 'mean_altitude')
        self.apoapsis = self.conn.add_stream(getattr, self.vessel.orbit, 'apoapsis_altitude')
        self.periapsis = self.conn.add_stream(getattr, self.vessel.orbit, 'periapsis_altitude')

        ## deprecated by get_srb_fuel() method
        # self.stage_4_resources = self.vessel.resources_in_decouple_stage(stage=4, cumulative=False)
        # self.srb_fuel = self.conn.add_stream(self.stage_4_resources.amount, 'SolidFuel')

    def select_craft_config(self):

        craft_name = krpc.connect().space_center.active_vessel.name
        resources_dir = os.path.join(os.getcwd(), r"..\resources")

        for json_config_file in os.listdir(resources_dir):

            json_config_craft_name = json_config_file.split('_config.json')[0]
            if json_config_craft_name.lower() == craft_name.lower():
                print("Loading config file {}".format(json_config_file))
                return os.path.join(resources_dir, json_config_file)

            else:
                raise Exception("Could not find config file for craft {}".format(craft_name))
                # todo implement below
                return self.create_new_config(craft_name)

    # todo add
    def create_new_config(self, craft_name):

        # make a new json file using craft name
        # for each param in json, populate details and enforce type

        new_craft_config = os.path.join(os.getcwd(), 'r..\resources', craft_name.lower(), "_config.json")

        with open(new_craft_config, 'w') as new_craft_json:
            # open template and loop? then save as new file




    ## SAS stuff
    ## fixme - get one method working and pass in SAS mode. output below, how to get enum?
    ## (Pdb) self.vessel.control.sas_mode = "prograde"
    ## *** TypeError: SpaceCenter.Control_set_SASMode() argument 1 must be a <enum 'SASMode'>, got a <class 'str'>

    def set_sas(self, sasMode):
        self.vessel.auto_pilot.disengage()
        self.vessel.control.sas = True
        time.sleep(0.1)
        breakpoint()
        self.vessel.control.sas_mode = self.vessel.control.sas_mode.sasMode

        ## todo try using autopilot commands in krpc

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

    # ## deprecated
    # def get_srb_fuel(self, srb_decouple_stage, fuel_type):
    #     stage_resources = self.vessel.resources_in_decouple_stage(stage=srb_decouple_stage, cumulative=False)
    #     srb_fuel = self.conn.add_stream(stage_resources.amount, 'SolidFuel')
    #
    #     return srb_fuel()

    # todo part_name is not very specific and will probably break easily
    # todo add functionality to account for not all engines of one type being expended in current stage (as above method)
    def get_fuel_in_stage(self, part_name, fuel_type):
        stage_resources = self.vessel.parts.in_stage(self.vessel.control.current_stage)
        total_fuel = 0
        for part in stage_resources:
            if part_name in part.name:
                total_fuel += part.resources.amount(name = fuel_type)

        return total_fuel

class Launcher(Core):


    def __init__(self, target_apo=100000, target_peri=100000):

        """
        :param alt_turn_start: self explanatory
        :param alt_turn_end: the craft will turn in order to hit final_pitch by this altitude
        :param final_pitch: in degrees. this pitch will be held until target_apo is reached
        :param warp: timewarp 0-3 = 1-4x
        :param srbs_separated: default False means the solid fuel boosters in current stage will be staged when empty
        :param lf_launch_stage_expended: default False means the liquid fuel booster in current stage will be staged when empty
        :return:
        """

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

    def gravity_turn(self):

        turn_angle = 0

        self.vessel.auto_pilot.engage()
        self.vessel.auto_pilot.target_pitch_and_heading(90, 90)

        while self.altitude() < 0.9*self.alt_turn_start:
            pass

        self.set_phys_warp(self.warp)

        print("Entering gravity turn loop")
        while True:

            if self.altitude() > self.alt_turn_start and self.altitude() < self.alt_turn_end:
                frac = ((self.altitude() - self.alt_turn_start) / (self.alt_turn_end - self.alt_turn_start))
                new_turn_angle = frac * 90
                if abs(new_turn_angle - turn_angle) > 0.5:
                    turn_angle = 90-new_turn_angle + frac*self.final_pitch
                    self.vessel.auto_pilot.target_pitch_and_heading(turn_angle, 90)

            if not self.srbs_separated:
                if self.get_fuel_in_stage("solid", "SolidFuel") < 0.1:
                    print("Staging SRBs done")
                    self.vessel.control.activate_next_stage()
                    self.srbs_separated = True

            if not self.lf_launch_stage_expended:
                if self.get_fuel_in_stage("LFB", "LiquidFuel") < 0.1:
                    self.vessel.control.activate_next_stage()
                    self.lf_launch_stage_expended = True

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
        self.vessel.auto_pilot.engage()
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


        print('Launch complete')
        time.sleep(1)
        self.sas_prograde()


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
        remaining_burn = self.conn.add_stream(node.remaining_burn_vector, node.reference_frame)

        while remaining_burn()[1] > 0.1:
            pass
        self.vessel.control.throttle = 0.0
        node.remove()
        self.sas_prograde()


class Transfer(Core):

    def execute_node(self):
        pass


def main():

    # moonsat1_json = os.path.join(os.getcwd(), r"..\resources\moonsat1_config.json")

    launcher = Launcher()
    orbit = Orbit()

    launcher.launch()
    # launcher.gravity_turn_no_staging()
    launcher.gravity_turn()
    launcher.circularise()

def test():

    test = Core()
    test.set_sas(prograde)

if __name__ == "__main__":

    main()
