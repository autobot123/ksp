import krpc
import time
import math
import json
import os
from json_config_creator import JsonConfigCreator
import decimal

# todo add target apo and peri to class

"""
cmd line:
from krpc_FUNCTIONS import Core, Launcher, Orbit
"""


class Core:

    def __init__(self):

        self.craft_name = krpc.connect(name="get_craft_name").space_center.active_vessel.name
        # try to remove get_craft_name script created by above code
        krpc.connect("get_craft_name").close()

        # setting up craft config
        json_config = self.select_craft_config()
        with open(json_config, "r") as json_file:
            craft_params = json.load(json_file)
        self.craft_params = craft_params
        self.launch_params = self.craft_params['launch_params']

        # connections
        self.conn = krpc.connect(name=self.craft_name)
        self.canvas = self.conn.ui.stock_canvas
        self.vessel = self.conn.space_center.active_vessel
        self.srf_frame = self.vessel.orbit.body.reference_frame

        # flight info
        self.ut = self.conn.add_stream(getattr, self.conn.space_center, 'ut')
        self.altitude = self.conn.add_stream(getattr, self.vessel.flight(), 'mean_altitude')
        self.apoapsis = self.conn.add_stream(getattr, self.vessel.orbit, 'apoapsis_altitude')
        self.periapsis = self.conn.add_stream(getattr, self.vessel.orbit, 'periapsis_altitude')

    def select_craft_config(self):

        craft_config_template = r'..\resources\craft_config\craft_config_template.json'

        craft_config_filepath = os.path.join(os.getcwd(), r"..\resources\craft_config", self.craft_name.lower() + "_config.json")

        if os.path.exists(craft_config_filepath):
            query_response = input("Config found. Modify? y/n\n")
            while True:
                if query_response == "y":
                    configCreator = JsonConfigCreator(craft_config_filepath, craft_config_filepath)
                    configCreator.create_new_craft_config()
                    return craft_config_filepath
                elif query_response == "n":
                    print("Loading craft config {}".format(craft_config_filepath))
                    return craft_config_filepath
                else:
                    query_response = input("Invalid input. Please enter y or n\n")
                    continue

        else:
            print("Could not find config file for craft {}. Generating new config...".format(self.craft_name))
            configCreator = JsonConfigCreator(craft_config_template, craft_config_filepath)
            configCreator.create_new_craft_config()
            return craft_config_filepath

        # for json_config_file in os.listdir(craft_config_dir):
        #     json_config_craft_name = json_config_file.split('_config.json')[0]
        #     print(json_config_craft_name)
        #     if json_config_craft_name.lower() == craft_name.lower():
        #         print("Loading config file {}".format(json_config_file))
        #         return os.path.join(craft_config_dir, json_config_file)
        #
        #     else:
        #         #raise Exception("Could not find config file for craft {}".format(craft_name))
        #         # todo implement below
        #         return self.create_new_config(craft_name)

    def set_orientation(self, direction):
        """
        :param direction: see dict below for possible strings
        :return:
        """

        direction_mod1 = direction.lower()
        direction_mod1.replace("-", "_")
        direction_dict = {"prograde": "normal",
                          "retrograde": "anti_normal",
                          "normal": "prograde",
                          "anti_normal": "retrograde",
                          "radial": "radial",
                          "anti_radial": "anti_radial"}

        if direction_mod1 not in direction_dict.keys():
            raise Exception(f"Invalid direction: {direction}")

        # adjust direction (pro/retrograde actually point normal/anti-normal and vice versa)
        direction_mod2 = direction_dict[direction]

        self.enable_autopilot()

        # set direction
        ref_frame = self.vessel.orbital_reference_frame
        direction_stream = self.conn.add_stream(getattr, self.vessel.flight(ref_frame), direction_mod2)
        self.vessel.auto_pilot.target_direction = direction_stream()

        # wait for vessel to lineup
        self.vessel.auto_pilot.wait()
        print(f"Vessel oriented to {direction_stream}")

        # todo test what happens if I remove stream?

    def activate_stage(self, msg, delay=0.5):
        time.sleep(delay)
        print(msg)
        self.vessel.control.activate_next_stage()

    def enable_sas(self):
        if not self.vessel.control.sas:
            self.vessel.auto_pilot.disengage()
            self.vessel.control.sas = True
            time.sleep(0.1)

    def enable_autopilot(self):
        if self.vessel.control.sas:
            self.vessel.control.sas = False
        self.vessel.auto_pilot.engage()

    def set_sas(self, sasMode):
        self.enable_sas()
        breakpoint()
        self.vessel.control.sas_mode = self.vessel.control.sas_mode.sasMode

    def sas_prograde(self):
        self.enable_sas()
        self.vessel.control.sas_mode = self.vessel.control.sas_mode.prograde

    def sas_target(self):
        self.enable_sas()
        self.vessel.control.sas_mode = self.vessel.control.sas_mode.target

    def set_pitch_heading(self, pitch, heading):
        self.enable_autopilot()
        self.vessel.auto_pilot.target_pitch_and_heading(pitch, heading)

    def set_phys_warp(self, factor=0):
        self.conn.space_center.physics_warp_factor = factor
        print(f"Warp factor: {factor+1}")

    ## todo test
    def get_fuel_quantity(self):
        solid_fuel = self.conn.get_call(self.vessel.resources.amount, "SolidFuel")
        liquid_fuel = self.conn.get_call(self.vessel.resources.amount, "LiquidFuel")
        return solid_fuel, liquid_fuel

    def warp_to(self, time):
        ## fixme below command unreliable
        self.conn.space_center.warp_to(time)
        ## todo use set_apo time warp in this method? work out how to scale warping

    # todo part_name is not very specific and will probably break easily
    # todo add functionality to account for not all engines of one type being expended in current stage (as above method)
    def get_fuel_in_stage(self, part_name, fuel_type, print_fuel=False):
        stage_resources = self.vessel.parts.in_stage(self.vessel.control.current_stage)
        total_fuel = 0
        for part in stage_resources:
            if part_name in part.name:
                total_fuel += part.resources.amount(name=fuel_type)

        if print_fuel:
            print("{}: {}".format(fuel_type, total_fuel))
        return total_fuel

    def print_float(self, msg, num, decimal_places, units):
        print(f"{msg}{round(num,decimal_places)}{units}")


    # todo TEST THIS
    def execute_next_node(self):
        # get next node
        nodes = self.vessel.control.nodes
        next_node = nodes[0]
        delta_v = next_node.delta_v
        self.print_float("node delta V: ", delta_v, 3, "m/s")
        # print(f"node delta V: {delta_v}")

        self.enable_autopilot()

        # point ship at node
        # todo match with set_orientation? add set_ref_frame method?
        self.vessel.auto_pilot.reference_frame = next_node.reference_frame
        self.vessel.auto_pilot.target_direction = (0, 1, 0)
        self.vessel.auto_pilot.wait()

        # calculate burn time
        F = self.vessel.available_thrust
        Isp = self.vessel.specific_impulse * 9.82
        m0 = self.vessel.mass
        m1 = m0 / math.exp(delta_v / Isp)
        flow_rate = F / Isp
        burn_time = (m0 - m1) / flow_rate

        self.print_float("Burn time: ", burn_time, 3, " seconds")

        # Wait until burn
        # todo make sure burn_ut > ut(). otherwise burn is in the past and process should exit.
        burn_ut = next_node.ut

        lead_time = 5
        self.print_float("Warp to ", lead_time, 1, " seconds to burn")
        # todo test this
        self.conn.space_center.warp_to(burn_ut - lead_time - burn_time)

        # Execute burn
        print('Ready to execute burn')
        # todo try converting to decimal here?
        burn_dv = self.conn.add_stream(getattr, next_node, "remaining_delta_v")

        # sleep until burn time
        while (burn_ut - self.ut()) - (burn_time / 2) > 0:
            countdown_to_burn = (burn_ut - self.ut()) - (burn_time / 2)
            # todo make it count 10, 9, 8 etc. but only print once
            #self.print_float("countdown to burn: ", countdown_to_burn, 3, " seconds")
            #time.sleep(0.1)
            pass

        self.print_float("Burning for ", burn_time, 3, " seconds")
        self.vessel.control.throttle = 1.0

        # todo turn into recursive method? to fine tune burning?

        new_burn_dv = 10000000
        decimal.getcontext().prec = 3
        while True:
            # multiply by 1 to ensure values are rounded as per precision above
            old_burn_dv = decimal.Decimal(new_burn_dv) * 1
            new_burn_dv = decimal.Decimal(burn_dv()) * 1
            ## debugging
            # print(f"old_burn_dv: {old_burn_dv}, new_burn_dv: {new_burn_dv}\n{new_burn_dv > old_burn_dv}")
            # time.sleep(0.1)
            if 5 < new_burn_dv < 20:
                self.vessel.control.throttle = 0.5
            elif 1 < new_burn_dv < 5:
                self.vessel.control.throttle = 0.1
            elif burn_dv() < 1:
                self.vessel.control.throttle = 0.01
            if new_burn_dv < 0.01:
                self.vessel.control.throttle = 0.0
                self.print_float("Final delta V remaining: ", new_burn_dv, 3, "m/s")
                break
            elif new_burn_dv > old_burn_dv:
                self.vessel.control.throttle = 0.0
                self.print_float("Final delta V remaining: ", new_burn_dv, 3, "m/s")
                break

        next_node.remove()
        print('Launch complete')
        time.sleep(1)
        self.sas_prograde()


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
        print("Launch stage complete")

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
                srb_fuel_amount = self.get_fuel_in_stage("solid", "SolidFuel")
                if srb_fuel_amount < 0.1:
                    self.activate_stage("*****Ditching SRBs*****")
                    self.srbs_separated = True

            if not self.lf_launch_stage_expended:
                lf_fuel_amount = self.get_fuel_in_stage("LFB", "LiquidFuel")
                if lf_fuel_amount < 0.1:
                    self.activate_stage("*****Ditching LF booster*****")
                    self.lf_launch_stage_expended = True

            if self.apoapsis() > self.target_apo:
                break

            time.sleep(0.1)

        print("Gravity turn complete. Coasting to apoapsis")
        self.sas_prograde()
        self.vessel.control.throttle = 0

    ## DEPRECATED
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

    pass

def main():

    launcher = Launcher()
    #orbit = Orbit()

    launcher.launch()
    # launcher.gravity_turn_no_staging()
    launcher.gravity_turn()
    launcher.circularise()

def test():

    test = Core()

    test.execute_next_node()

    # # demonstration orientation
    # directions = ["normal", "anti_normal", "prograde", "retrograde", "radial", "anti_radial"]
    # for item in directions:
    #     print(item)
    #     test.set_orientation(item)


if __name__ == "__main__":

    test()
