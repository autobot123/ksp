to test:
- add method to get fuel amounts. GetFuelAmounts() as general method?


backlog:
- call info display script using sub process popen. program is python, first argument is my script https://stackoverflow.com/questions/7152340/using-a-python-subprocess-call-to-invoke-a-python-script
- change circularise method to match apoapsis. Cut throttle if app rises more then ten %
- add booster_separator(fuel_type, fuel_threshold)
- can the gravity turn logic go into its own method? Or is it better to have that written out and call the booster_sep method in the while loop?
- add more useful stats. vessel mass. some rocket equations? e.g. for circularisation burn
- remove Phys warp calls from other methods. Write out in launcher scripts


Launcher:

Gravity turn:
- enter num stages to stage during gravity turn
- enter type of fuel to monitor? or use GetFuelAmounts()?
- if using srbs, use srb_separator method. if LF, use lf_separator method.

circularise:
- create_node(mu=gravitational_parameter, r=apoapsis, a1=semi_major_axis, time_to_apo, prograde=delta_v?) method
- calculate_burn_time(grav_constant=9.82?, ) return burn_time
- orientate_ship(0, 0, 0) method 
- execute_burn(time_to_burn) - how to confirm burn finished? pass in parameter and value, e.g. parameter=periapsis and value= 0.99*target_periapsis?
- remove_node() method

use mock to test?

Test most efficient launch profiles
Could try quickly banking over to 45 degrees? Then follow prograde?


