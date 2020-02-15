import json
from typing import Any

from common.file_utils import make_if_not_exists


def read(json_path: str) -> str:
    with open(json_path, "r") as f:
        val = json.loads(f.read())
        return val


def write(json_path: str, val: Any, cls=json.JSONEncoder, mode: str = "w") -> None:
    make_if_not_exists(json_path)
    with open(json_path, mode) as f:
        json.dump(val, f, indent=4, cls=cls)
