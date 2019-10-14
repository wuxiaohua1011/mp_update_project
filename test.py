from models import *
from monty.io import zopen
import json
import requests as re
from jsondiff import diff
with zopen("data/more_mats.json") as f:
    parsed = json.load(f)


def test_get_formula():
    try:
        response = re.get('http://127.0.0.1:8000/materials/formula/Ta*')
        material = Material(**parsed[46])
        json_a = material.json()
        json_b = response.json()[0]
        print(diff(json_a, json_b)) # ?????
    except re.exceptions.ConnectionError as e:
        assert False, "Did you start the server?"

test_get_formula()

