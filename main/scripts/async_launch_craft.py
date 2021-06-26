import asyncio
from functions.async_launcher import AsyncLauncher


async def launch(orientation):

    print("Running async launcher script")

    # 0 for polar orbit, 90 for conventional
    launcher = AsyncLauncher(compass_heading=orientation)
    launcher.launch(warp=0)

    await asyncio.gather(launcher.monitor_launch_state(),
                         launcher.async_stage_when_engine_empty(),
                         launcher.gravity_turn(),
                         launcher.circularise())

    print("Exiting async launcher script")


if __name__ == "__main__":

    # 0 for polar, 90 for standard
    orientation = 90

    asyncio.run(launch(orientation))
