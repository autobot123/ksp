# Random notes from reading Kroc GitHub/discord/etc.

- use with statement to close stream after code block

```python
conn = krpc.connect()
vessel = conn.space_center.active_vessel
refframe = vessel.orbit.body.reference_frame
with conn.stream(vessel.position, refframe) as position:
    while True:
        print(position())
```

- get position of vehicle
```python
conn = krpc.connect()
vessel = conn.space_center.active_vessel
refframe = vessel.orbit.body.reference_frame
position = conn.add_stream(vessel.position, refframe)
while True:
    print(position())
```
