import asyncio
from functions.async_launcher import AsyncLauncher


"""
need two functions:
- staging
- turning

then use async.gather(staging, turning)
"""


# fixme - still waiting for stage_when_empty to finish. how do I solve this?

async def main():

    print("Running async launcher script")
    launcher = AsyncLauncher()
    launcher.launch(warp=1)

    await asyncio.gather(launcher.async_stage_when_engine_empty(), launcher.gravity_turn())
    print("Exiting async launcher script")


if __name__ == "__main__":
    asyncio.run(main())
