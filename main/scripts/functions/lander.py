from .core import Core
import time


class Lander(Core):

    #todo: use terrain altitude to fine tune suicide burn (e.g. work out time to impact, account for the acceleration from the engine)

    def __init__(self):
        super().__init__()

    def suicide_burn(self):

        # todo deploy chute

        print("Initiating suicide burn, waiting for altitude to drop")
        self.enable_sas()
        self.vessel.control.sas_mode = self.vessel.control.sas_mode.retrograde
        while self.surface_altitude() > 2750:
            pass

        print(f"Altitude below {self.surface_altitude():.2f}, entering burn loop")
        while True:

            # todo work out how to tailor for landing
            # todo throttle += 0.01 based on how fast vert speed goes up or down?
            # make it descend at 20m/s below 500m, then 10m/s below 100, then 5 below 25

            if self.vertical_speed() < -30:
                self.vessel.control.throttle = 1
                # print(f"vert speed = {self.vertical_speed()}. Throttle set to {self.vessel.control.throttle}")
            elif -30 <= self.vertical_speed() < -10:
                self.vessel.control.throttle = 0.45
                # print(f"vert speed = {self.vertical_speed()}. Throttle set to {self.vessel.control.throttle}")
            elif -10 <= self.vertical_speed() < -5:
                self.vessel.control.throttle = 0.17
                # print(f"vert speed = {self.vertical_speed()}. Throttle set to {self.vessel.control.throttle}")
            else:
                self.vessel.control.throttle = 0.05
                # print(f"vert speed = {self.vertical_speed()}. Throttle set to {self.vessel.control.throttle}")

            if self.surface_altitude() < 5 and self.vertical_speed() > -2:
                break

            time.sleep(0.1)

        self.vessel.control.throttle = 0
        print("Vessel landed")

    def suicide_burn_v2(self, suicide_burn_alt):
        """
        todo
        add event support
        add better logic for tapering throttle
        auto calculate throttle required to maintain vertical speed
        taper final stage of landing

        :param suicide_burn_alt:
        :return:
        """

        print("Initiating suicide burn, waiting for altitude to drop")
        self.enable_sas()
        self.vessel.control.sas_mode = self.vessel.control.sas_mode.retrograde

        # expr = self.conn.krpc.Expression.less_than(self.conn.krpc.Expression.call(self.surface_altitude()),
        #                                            suicide_burn_alt)
        # suicide_burn_alt_event = self.conn.krpc.add_event(expr)
        # with suicide_burn_alt_event.condition:
        #     suicide_burn_alt_event.wait()

        while self.surface_altitude() > suicide_burn_alt:
            pass

        self.vessel.control.throttle = 1

        # expr = self.conn.krpc.Expression.less_than(self.conn.krpc.Expression.call(self.vertical_speed()), 0)
        # engine_cut_event = self.conn.krpc.add_event(expr)
        # with engine_cut_event.condition:
        #     engine_cut_event.wait()

        while self.vertical_speed() < -10:
            pass

        self.vessel.control.throttle = 0

        while self.vessel.situation.name != "landed":

            if self.vertical_speed() < -10:
                self.vessel.control.throttle += 0.05

            if self.vertical_speed() < -5:
                self.vessel.control.throttle += 0.01

            if self.vertical_speed() > -2:
                self.vessel.control.throttle -= 0.25

            time.sleep(0.05)

        print("landed")
        self.vessel.control.throttle = 0
