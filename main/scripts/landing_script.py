import asyncio
from functions.lander import Lander


print("Running landing script")
lander = Lander()

# lander.execute_next_node()

lander.suicide_burn()

print("Exiting landing script")
