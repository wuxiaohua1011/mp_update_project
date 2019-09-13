from monty.io import zopen
import json
from models import *
from fastapi.encoders import jsonable_encoder

with zopen("data/material_docs.json") as f:
    data = f.read()

parsed = json.loads(data)
first_material = parsed[0]
first_material_model = Material(**first_material)


