import asyncio
from functions.lander import Lander


print("Running landing script")
lander = Lander()

# lander.execute_next_node()

# lander.suicide_burn()
# lander.execute_next_node()

# suicide burn alt 1771
lander.suicide_burn(900)

print("Exiting landing script")


class ClassName:

    def __init__(self):
        self.my_attr = my_attr
