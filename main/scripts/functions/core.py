import krpc
import time
import math
import json
import os
from json_config_creator import JsonConfigCreator
import decimal

# todo add target apo and peri to class


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
        orbit_body_ref_frame = self.vessel.orbit.body.reference_frame
        self.vertical_speed = self.conn.add_stream(getattr, self.vessel.flight(orbit_body_ref_frame), 'vertical_speed')

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
        print("Engaging KRPC auto pilot")
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


    def calculate_burn_time(self, delta_v):
        F = self.vessel.available_thrust
        Isp = self.vessel.specific_impulse * 9.82
        m0 = self.vessel.mass
        m1 = m0 / math.exp(delta_v / Isp)
        flow_rate = F / Isp
        burn_time = (m0 - m1) / flow_rate

        return burn_time

    def get_active_engine_info(self):
        pass

        # if no active engine, warning

    # todo TEST THIS
    def execute_next_node(self):

        self.get_active_engine_info()

        # get next node
        nodes = self.vessel.control.nodes
        next_node = nodes[0]
        delta_v = next_node.delta_v
        self.print_float("Node delta V: ", delta_v, 3, "m/s")

        # todo check if node will require staging. if so, add staging and calculate next stages delta_v
        # add method to calculate delta_v remaining in stage?

        self.enable_autopilot()

        # point ship at node
        # todo match with set_orientation? add set_ref_frame method?
        self.vessel.auto_pilot.reference_frame = next_node.reference_frame
        self.vessel.auto_pilot.target_direction = (0, 1, 0)
        self.vessel.auto_pilot.wait()

        # calculate burn time
        burn_time = self.calculate_burn_time(delta_v)

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
            if 5 < new_burn_dv < 20:
                self.vessel.control.throttle = 0.5
            elif 1 < new_burn_dv < 5:
                self.vessel.control.throttle = 0.2
            elif burn_dv() < 0.5:
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


if __name__ == "__main__":

    test()
