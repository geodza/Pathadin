import json

from file_utils import make_if_not_exists


def read(json_path):
    with open(json_path, "r") as f:
        val = json.loads(f.read())
        return val


def write(json_path, val, mode="w"):
    make_if_not_exists(json_path)
    with open(json_path, mode) as f:
        json.dump(val, f, indent=4)
