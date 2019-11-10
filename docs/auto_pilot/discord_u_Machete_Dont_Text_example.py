import krpc
import time

conn = krpc.connect(name='Re-entry')
vessel = conn.space_center.active_vessel

ap = vessel.auto_pilot # because I'm lazy
ref_frame = vessel.orbital_reference_frame

altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
retrograde = conn.add_stream(getattr, vessel.flight(ref_frame), 'anti_normal') # have to pass ref frame to flight

ap.reference_frame = ref_frame
ap.engage()

while altitude() > 30000:
    ap.target_direction = (retrograde())
    ap.wait() # let the craft settle down. It'll pause the loop while the craft rotates.
    time.sleep(0.1)

ref_frame = vessel.surface_reference_frame
retrograde.remove() # because I'm anal-retentive
retrograde = conn.add_stream(getattr, vessel.flight(ref_frame), 'retrograde')
ap.reference_frame = ref_frame

while altitude() > 12000:
    ap.target_direction = (retrograde())
    ap.wait()
    time.sleep(0.1)

print('Re-entry to safe altitude complete, disabling control')
for parachute in vessel.parts.parachutes:
    parachute.deploy()