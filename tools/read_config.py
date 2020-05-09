import json


def read_config(config_file_name='./config.json'):
    with open(config_file_name, 'r') as file:
        config = json.load(file)
    return config
