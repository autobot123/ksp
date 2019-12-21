import asyncio
from functions.async_launcher import AsyncLauncher


async def main():

    print("Running async launcher script")
    launcher = AsyncLauncher()
    launcher.launch(warp=0)

    await asyncio.gather(launcher.async_stage_when_engine_empty(), launcher.gravity_turn())
    launcher.circularise()
    print("Exiting async launcher script")


if __name__ == "__main__":
    asyncio.run(main())
