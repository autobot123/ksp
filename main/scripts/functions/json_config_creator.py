import json
from pprint import pprint

# todo - use ship name as script name?
# fixme - check type of values entered


class JsonConfigCreator:

    def __init__(self, craft_config_template, new_craft_config_file):
        self.new_craft_config_file = new_craft_config_file
        self.craft_config_template = craft_config_template
        with open(self.craft_config_template, 'r') as f:
            self.config_data = json.load(f)

        # fixme delete?
        self.new_dict = {}

    def param_validator(self):
        # todo check entered values against the parameters stored in json files? or do that inline and add type to template file?
        pass

    def create_new_craft_config(self):
        print("TEMPLATE CONFIG: \n")
        pprint(dict(self.config_data))
        print()

        # new_config_data = self.create_new_dict(self.data)
        self.create_new_dict(self.config_data)

        print("OUTPUT DATA: \n")
        pprint(dict(self.config_data))

        self.write_new_config_to_file(self.config_data)

    def edit_param(self, key, value):

        while value == "":
            new_value = input(f"'{key}' is blank. Enter a value:\n")
            if new_value != "":
                return new_value
            else:
                print("Error: blank input. Try again")
                continue

        query_response = input(f"'{key}': '{value}'. Modify? y / n\n")
        while True:
            if query_response == "y":
                new_value = input("Type the new value\n")
                print("New value: {}".format(new_value))
                return new_value
            elif query_response == "n":
                return value
            else:
                query_response = input("Invalid input. Please enter y or n\n")
                continue

    # todo try passing in a blank dictionary and copying to that instead of editing dict_data in place?
    def create_new_dict(self, dict_data):

        for (key, param) in dict_data.items():
            if type(param) is not dict:
                param_type = type(param)
                new_param = param_type(self.edit_param(key, param))
                print(f"New parameter = {new_param} {type(new_param)}")
                dict_data[key] = new_param
            elif type(param) is dict:
                print("***EDITING {}***\n".format(key.upper()))
                self.create_new_dict(param)
                print("current dict: ", dict_data)
                # self.create_new_dict(value)

        return dict_data

    # todo fix so that it overwrites existing files if modified
    def write_new_config_to_file(self, new_config_data):
        with open(self.new_craft_config_file, "w") as outfile:
            json.dump(new_config_data, outfile, indent=2)


def main():

    craft_config_template = r"C:\projects\ksp\main\resources\craft_config\craft_config_template.json"
    new_craft_config = r"C:\projects\ksp\main\resources\craft_config\test_config.json"

    test = JsonConfigCreator(craft_config_template, new_craft_config)
    test.create_new_craft_config()

def test():
    craft_config_template = r"C:\projects\ksp\main\resources\craft_config\craft_config_template.json"
    new_craft_config = r"C:\projects\ksp\main\resources\craft_config\test_config.json"

    test = JsonConfigCreator(craft_config_template, new_craft_config)
    test.create_new_craft_config()


if __name__ == "__main__":
    test()
