#Reference Frames

In the orbital reference frame, the y axis points prograde
In the surface reference frame,  







##### anti-normal
self.vessel.auto_pilot.target_direction = self.vessel.flight().prograde
##### normal
self.vessel.auto_pilot.target_direction = self.vessel.flight().retrograde
# ####prograde
self.vessel.auto_pilot.target_direction = self.vessel.flight().normal
##### retrograde
self.vessel.auto_pilot.target_direction = self.vessel.flight().anti_normal
##### radial
self.vessel.auto_pilot.target_direction = self.vessel.flight().radial
##### anti-radial
self.vessel.auto_pilot.target_direction = self.vessel.flight().anti_radial



# Reference Frames

##### set reference frame
self.vessel.auto_pilot.reference_frame = self.vessel.surface_velocity_reference_frame