## Get orbital velocity
https://forum.kerbalspaceprogram.com/index.php?/topic/62902-14x13x122-krpc-remote-procedure-call-server-v047-27th-july-2018/page/13/
    
    On 1/31/2016 at 9:00 PM, Kobymaru said:

    Hi! In the python client, when I try to read, conn.space_center.active_vessel.orbit.speed, the value always stays the same, even if in KSP the speed changes.

    Is this a bug or did I misunderstand something?

For me, it always returns 0. They must have changed something in KSP since I implemented it... The code was using Orbit.orbitalSpeed. Changing it to use Orbit.vel.magnitude (as suggested on the community API docs) appears to fix the issue. Here's a link to KRPC.SpaceCenter.dll with the fix applied:

https://github.com/djungelorm/krpc/files/111770/KRPC.SpaceCenter.dll.zip

Let me know if that works for you.
