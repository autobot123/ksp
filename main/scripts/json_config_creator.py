import os
import json
from pprint import pprint

craft_config_template = r"C:\projects\ksp\main\resources\craft_config\craft_config_template.json"

with open(craft_config_template, 'r') as f:
    data = json.load(f)

print(data, "\n")


def edit_param(key, value):

    value_edited = False
    
    while value == "":
        value = input("{} is blank, please enter a value\n".format(key))
        if value != "":
            data[key] = value
            value_edited = True
        else:
            value_edited = True
            print("Blank input is not allowed. Please try again")
            continue
        
    if value_edited != True:
        query_response = input("'{}': '{}'. Would you like to modify the value? y / n\n".format(key, value))
        if query_response == "y":
            data[key] = input("Type the new value\n")
            print("New value: {}".format(data[key]))

for (key, value) in data.items():

    print("Key: '{}', value: '{}'".format(key, value))

    if type(value) is str:
        edit_param(key, value)
            
    elif type(value) is int:
        edit_param(key, value)
        
    elif type(value) is dict:
        #print("{} is an dict".format(v))
        for (key2, value2) in value.items():
            edit_param(key2, value2)
            #print("{}: {}".format(key2, value2))
            
    else:
        raise Exception("Unknown type for value {}".format(value))

print()
pprint(dict(data.items()))


#make a new dictionary and copy values to it. solves the RuntimeError: dictionary changed size during iteration
