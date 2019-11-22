"""
todo:
add dV remaining

"""




import krpc
import time
import math
from pdb import set_trace as breakpoint

conn = krpc.connect(name='Info display')
canvas = conn.ui.stock_canvas
vessel = conn.space_center.active_vessel
srf_frame = vessel.orbit.body.reference_frame

screen_size = canvas.rect_transform.size
panel_main = canvas.add_panel()

rect = panel_main.rect_transform
rect.size = (300,200)
rect.position = (160-(screen_size[0]/2),280)

panel_phr = canvas.add_panel()
rect_phr= panel_phr.rect_transform
rect_phr.size = (300, 200)
rect_phr.position = (1080 - (screen_size[0] / 2), 330)

# launch button
button = panel_main.add_button("Launch")
button.rect_transform.position = (-50,70)

def main_info(txt="Attr: %d unit", x=-50, y=0, color=(1,1,1), size=18):
    tele = panel_main.add_text(txt)
    tele.rect_transform.position = (x, y)
    tele.color = color
    tele.size = size
    return tele
	
def phr_info(txt="Attr: %d unit", x=-50, y=0, color=(1, 1, 1), size=18):
    tele = panel_phr.add_text(txt)
    tele.rect_transform.position = (x, y)
    tele.color = color
    tele.size = size
    return tele

# main info
thrust = main_info(y=32)
speed = main_info(y=12)
alt_agl = main_info(y=-8)
apo = main_info(y=-28)
peri = main_info(y=-48)
time_apo = main_info(y=-68)
time_peri = main_info(y=-88)

# directional info
pitch_info = phr_info(y=75)
heading_info = phr_info(y=55)
roll_info = phr_info(y=35)

# Set up a stream to monitor the throttle button
button_clicked = conn.add_stream(getattr, button, 'clicked')

###### Pitch, heading and roll

def cross_product(u, v):
    return (u[1]*v[2] - u[2]*v[1],
            u[2]*v[0] - u[0]*v[2],
            u[0]*v[1] - u[1]*v[0])

def dot_product(u, v):
    return u[0]*v[0] + u[1]*v[1] + u[2]*v[2]

def magnitude(v):
    return math.sqrt(dot_product(v, v))

def angle_between_vectors(u, v):
    """ Compute the angle between vector u and v """
    dp = dot_product(u, v)
    if dp == 0:
        return 0
    um = magnitude(u)
    vm = magnitude(v)
    return math.acos(dp / (um*vm)) * (180. / math.pi)


# launch info
while True:
    # Handle the throttle button being clicked
    if button_clicked():
        vessel.control.throttle = 1
        button.clicked = False

    # main info
    thrust.content = 'Thrust: %d kN' % (vessel.thrust/1000)
    speed.content = 'Speed: %d m/s' % (vessel.flight(srf_frame).speed)
    alt_agl.content = 'Altitude: %d m' % (vessel.flight(srf_frame).surface_altitude)
    apo.content = "Apoapsis: %d m" % (vessel.orbit.apoapsis_altitude)
    peri.content = "Periapsis: %d m" % (vessel.orbit.periapsis_altitude)
    time_apo.content = "Time to Apo: %d s" % (vessel.orbit.time_to_apoapsis)
    time_peri.content = "Time to Peri: %d s" % (vessel.orbit.time_to_periapsis)


    ##################################################################
    # pitch, heading and roll
    vessel_direction = vessel.direction(vessel.surface_reference_frame)

    # Get the direction of the vessel in the horizon plane
    horizon_direction = (0, vessel_direction[1], vessel_direction[2])

    # Compute the pitch - the angle between the vessels direction and
    # the direction in the horizon plane
    pitch = angle_between_vectors(vessel_direction, horizon_direction)
    if vessel_direction[0] < 0:
        pitch = -pitch

    # Compute the heading - the angle between north and
    # the direction in the horizon plane
    north = (0, 1, 0)
    heading = angle_between_vectors(north, horizon_direction)
    if horizon_direction[2] < 0:
        heading = 360 - heading

    # Compute the roll
    # Compute the plane running through the vessels direction
    # and the upwards direction
    up = (1, 0, 0)
    plane_normal = cross_product(vessel_direction, up)
    # Compute the upwards direction of the vessel
    vessel_up = conn.space_center.transform_direction(
        (0, 0, -1), vessel.reference_frame, vessel.surface_reference_frame)
    # Compute the angle between the upwards direction of
    # the vessel and the plane normal
    roll = angle_between_vectors(vessel_up, plane_normal)
    # Adjust so that the angle is between -180 and 180 and
    # rolling right is +ve and left is -ve
    if vessel_up[0] > 0:
        roll *= -1
    elif roll < 0:
        roll += 180
    else:
        roll -= 180

    print('pitch = % 5.1f, heading = % 5.1f, roll = % 5.1f' %
          (pitch, heading, roll))
    pitch_info.content = 'Pitch: %d degrees'%(pitch)
    heading_info.content = 'Heading: %d degrees' % (heading)
    roll_info.content = 'Roll: %d degrees' % (roll)

    time.sleep(1)
