import krpc
import time
import math


class Launcher:

    def __init__(self, sas_activated, launch_num_stages):
        # connections
        self.conn = krpc.connect(name='Sub-orbital flight')
        self.canvas = self.conn.ui.stock_canvas
        self.vessel = self.conn.space_center.active_vessel
        self.srf_frame = self.vessel.orbit.body.reference_frame

        # launch parameters
        self.launch_num_stages = launch_num_stages
        self.vessel.control.sas = sas_activated

        # flight info
        self.ut = self.conn.add_stream(getattr, self.conn.space_center, 'ut')
        self.altitude = self.conn.add_stream(getattr, self.vessel.flight(), 'mean_altitude')
        self.apoapsis = self.conn.add_stream(getattr, self.vessel.orbit, 'apoapsis_altitude')
        self.stage_1_resources = self.vessel.resources_in_decouple_stage(stage=1, cumulative=False)
        self.srb_fuel = self.conn.add_stream(self.stage_1_resources.amount, 'SolidFuel')
        self.turn_angle = 0

        # # screen info
        # panel = self.canvas.add_panel()
        # screen_size = self.canvas.rect_transform.size
        # rect = panel.rect_transform
        # rect.size = (170, 40)
        # rect.position = (720- (screen_size[0] / 2), 280)
        #
        # button = panel.add_button("Launch")
        # button.rect_transform.position = (0, 0)
        # button_clicked = self.conn.add_stream(getattr, button, 'clicked')

        # # wait for launch
        # while True:
        #     if button_clicked():
        #         self.launch_it()
        #         button.clicked = False
        #         # todo destroy button?
        #         rect = None
        #         break
        #
        #     time.sleep(1)

    def print_info(self):
        while True:
            print(self.altitude())
            print(self.apoapsis())
            # print(self.stage_2_resources)
            print(self.srb_fuel())
            time.sleep(1)

    def launch_it(self):
        self.set_phys_warp(3)
        # self.conn.space_center.physics_warp_factor = 0
        print("Launching vessel")
        self.vessel.control.throttle = 1
        for i in range(self.launch_num_stages):
            self.vessel.control.activate_next_stage()
        self.vessel.control.sas = True
        time.sleep(0.1)

    # fixme delete
    def grav_turn(self, altitude_start, altitude_finish=0):
        mean_altitude = self.conn.get_call(getattr, self.vessel.flight(), 'mean_altitude')
        expr = self.conn.krpc.Expression.greater_than(self.conn.krpc.Expression.call(mean_altitude),
                                                 self.conn.krpc.Expression.constant_double(altitude_start))
        event = self.conn.krpc.add_event(expr)
        with event.condition:
            event.wait()
        print("Executing gravity turn")
        self.vessel.auto_pilot.engage()
        time.sleep(0.1)
        self.vessel.auto_pilot.target_pitch_and_heading(45, 90)

    #todo finish
    def grav_turn_gradual(self, alt_turn_start=5000,
                          alt_turn_end=30000,
                          target_apo=80000,
                          final_pitch=30,
                          warp=0):

        srbs_separated = False


        self.vessel.auto_pilot.engage()
        self.vessel.auto_pilot.target_pitch_and_heading(90, 90)

        while self.altitude() < 0.9*alt_turn_start:
            pass

        self.set_phys_warp(warp)

        while True:

            if self.altitude() > alt_turn_start and self.altitude() < alt_turn_end:
                frac = ((self.altitude() - alt_turn_start) / (alt_turn_end - alt_turn_start))
                new_turn_angle = frac * 90
                if abs(new_turn_angle - self.turn_angle) > 0.5:
                    turn_angle = 90-new_turn_angle + frac*final_pitch
                    self.vessel.auto_pilot.target_pitch_and_heading(turn_angle, 90)
                    # print("alt: {},    turn:{}".format(self.altitude(), turn_angle))

            if not srbs_separated:
                if self.srb_fuel() < 0.1:
                    print("SRBs done")
                    self.vessel.control.activate_next_stage()
                    self.vessel.control.activate_next_stage()
                    srbs_separated = True

            if self.apoapsis() > target_apo:
                break

            time.sleep(0.1)

        print("Gravity turn finished, coasting to apoapsis")
        self.sas_prograde()
        self.vessel.control.throttle = 0

    def circularise(self, target_peri=80000):

        while self.altitude() < 70000:
            pass

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

        print(burn_time)

        # todo add burn


    def separate_booster(self, num_stages, stage_desc="", fuel_cutoff=0.1):
        fuel_amount = self.conn.get_call(self.vessel.resources.amount, "SolidFuel")
        expr = self.conn.krpc.Expression.less_than(self.conn.krpc.Expression.call(fuel_amount),
                                                   self.conn.krpc.Expression.constant_float(fuel_cutoff))
        event = self.conn.krpc.add_event(expr)
        with event.condition:
            event.wait()
        print('Separating booster')
        for i in range(num_stages):
            self.vessel.control.activate_next_stage()
            if i < num_stages -1:
                print('Initiating {} stage'.format(stage_desc))

    def sas_prograde(self):
        self.vessel.auto_pilot.disengage()
        self.vessel.control.sas = True
        time.sleep(0.1)
        self.vessel.control.sas_mode = self.vessel.control.sas_mode.prograde

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
