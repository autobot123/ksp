backlog:
- Split maneuvres into maneuvre Class?
- List options when running script. E.g. do you want to launch(if you're on the launchpad)? Do you want to circularise?
- Do not launch if vehicle is not on launchpad
- If no config found, prompt to enter details
- Split out into different scripts as appropriate
- add craft files to repo and add installer method?
- refactor vessel orientation. can't get auto_pilot methods to work properly

major issue:
- two processes run when running krpc_FUNCTIONS. investigate - try calling from another script?
- streams d/c once script has finished. probably not an issue...

turn set_apo and set_peri into one method. define apo or peri in args.

to test:
- create gravity turn and manuever node only launch profile? stage myself
- add method to get fuel amounts. GetFuelAmounts() as general method?



backlog:
- call info display script using sub process popen. program is python, first argument is my script https://stackoverflow.com/questions/7152340/using-a-python-subprocess-call-to-invoke-a-python-script




User story: log flight data to CSV for analysis
Epic: automate landing on a body
Story: automatically control throttle to gradually reduce vertical speed when landing

Launcher:

circularise:
- create_node(mu=gravitational_parameter, r=apoapsis, a1=semi_major_axis, time_to_apo, prograde=delta_v?) method
- calculate_burn_time(grav_constant=9.82?, ) return burn_time
- orientate_ship(0, 0, 0) method 
- execute_burn(time_to_burn) - how to confirm burn finished? pass in parameter and value, e.g. parameter=periapsis and value= 0.99*target_periapsis?
- remove_node() method



