from functions.transfer import Transfer

print("Running transfer script")
transfer = Transfer()

# transfer.circularise_to_periapsis()
transfer.execute_next_node()

print("Exiting transfer script")
