from functions.orbit import Orbit


def main(total_delta_v, num_maneuvers):
    orbit = Orbit()
    orbit.multi_stage_transfer(total_delta_v, num_maneuvers)


if __name__ == "__main__":
    dV = 2434
    maneuvers = 8
    main(dV, maneuvers)
