import asyncio
from functions.lander import Lander


print("Running landing script")
lander = Lander()

# lander.execute_next_node()

# lander.suicide_burn()
# lander.execute_next_node()

# suicide burn alt 1771
lander.suicide_burn(2000)

print("Exiting landing script")
