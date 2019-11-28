from core import Core


class Lander(Core):

    def __init__(self):
        super().__init__()

    def suicide_burn(self):

        # todo deploy chute

        #self.set_orientation("retrograde")

        while self.altitude() > 2000:
            pass

        while True:

            if self.vertical_speed() > 100:
                self.vessel.control.throttle = 1
            elif 200 >= self.vertical_speed() > 30:
                self.vessel.control.throttle = 0.75
            elif 50 >= self.vertical_speed() > 10:
                self.vessel.control.throttle = 0.5
            else:
                self.vessel.control.throttle = 0.3

            if self.vertical_speed() == 0:
                break
