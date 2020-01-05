from .core import Core
import time


class Lander(Core):

    #todo: use terrain altitude to fine tune suicide burn (e.g. work out time to impact, account for the acceleration from the engine)

    def __init__(self):
        super().__init__()

    def suicide_burn(self, suicide_burn_alt):
        """
        todo
        add event support

        :param suicide_burn_alt:
        :return:
        """

        print("Initiating suicide burn, waiting for altitude to drop")
        self.enable_sas()
        self.vessel.control.sas_mode = self.vessel.control.sas_mode.retrograde

        while self.surface_altitude() > suicide_burn_alt and self.vertical_speed() > 0:
            pass
        print("Initiate landing burn at full throttle")
        self.vessel.control.throttle = 1

        while self.vertical_speed() < -10:
            pass
        print(f"Vertical speed {self.vertical_speed():.2f}. Maintaining constant vertical speed for landing.")
        self.adjust_throttle_for_twr(1)

        while self.surface_altitude() > 25:

            if -15 < self.vertical_speed() < -10:
                self.adjust_throttle_for_twr(1)
            elif self.vertical_speed() < -10:
                self.adjust_throttle_for_twr(1.1)
            elif self.vertical_speed() > -10:
                self.adjust_throttle_for_twr(0.5)
            time.sleep(0.05)

        print("final landing stage")
        while self.vessel.situation.name != "landed":

            if self.horizontal_speed() < 2:
                self.vessel.control.sas_mode = self.vessel.control.sas_mode.radial
            else:
                self.vessel.control.sas_mode = self.vessel.control.sas_mode.retrograde

            # initial figure (-5) is crucial, if this gap is too small the craft will overshoot into positive vertical speed
            if -5 < self.vertical_speed() < -2:
                self.adjust_throttle_for_twr(1.05)
            elif self.vertical_speed() > -2:
                self.vessel.control.throttle -= 0.5
            elif self.vertical_speed() < -5:
                self.vessel.control.throttle += 0.02

            time.sleep(0.05)

        print("landed")
        self.vessel.control.throttle = 0
