import asyncio
from functions.async_launcher import AsyncLauncher


# todo move this into async launcher?
async def main():

    print("Running async launcher script")
    launcher = AsyncLauncher(compass_heading=90)
    launcher.launch(warp=0)

    await asyncio.gather(launcher.monitor_launch_state(),
                         launcher.async_stage_when_engine_empty(),
                         launcher.gravity_turn(),
                         launcher.circularise())

    print("Exiting async launcher script")


if __name__ == "__main__":
    asyncio.run(main())
