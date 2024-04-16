import yaml


def load_yaml(yaml_file: str):
    with open(yaml_file, 'r') as file:
        return yaml.safe_load(file)
