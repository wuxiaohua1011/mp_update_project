from monty.io import zopen
import json
from models import *
from fastapi.encoders import jsonable_encoder

with zopen("data/material_docs.json") as f:
    data = f.read()

parsed = json.loads(data)
# first_material = parsed[0]
# first_material_model = Material(**first_material)

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hey, Michael was here LOL"}


@app.get("/task_id/{task_id}")
async def get_on_task_id(task_id: str):
    result = []
    for material in parsed:
        if material.get("task_id", None) == task_id:
            result.append(Material(**material))
    return {"found <{}> materials that matches task_id <{}>".format(len(result), task_id): result}


@app.get("/materials/")
async def get_on_chemsys(chemsys: str = ""):
    result = []
    input_chemsys_elements = set(chemsys.split("-"))

    for material in parsed:
        material_chemsys = set(material.get("chemsys").split("-"))
        if input_chemsys_elements & material_chemsys:
            result.append(material)
    return {"found <{}> materials that matches chemsys <{}>".format(len(result), chemsys): result}
