from monty.io import zopen
import json
from models import *
from fastapi.encoders import jsonable_encoder
from fastapi import Path
from starlette.responses import RedirectResponse, Response

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


@app.get("/materials/task_id/{task_id}")
async def get_on_task_id(task_id: str = Path(..., title="The task_id of the item to get")):
    result = []
    for material in parsed:
        if material.get("task_id", None) == task_id:
            result.append(Material(**material))
    return {"result": result}


@app.get("/materials/chemsys/{chemsys}")
async def get_on_chemsys(chemsys: str = Path(..., title="The task_id of the item to get")):
    result = []
    input_chemsys_elements = set(chemsys.split("-"))

    for material in parsed:
        material_chemsys = set(material.get("chemsys").split("-"))
        if input_chemsys_elements & material_chemsys:
            result.append(material)
    return {"result": result}


@app.get("/materials/formula/{formula}")
async def get_on_formula(formula: str = Path(..., title="The formula of the item to get")):
    result = ["not implemented"]
    return {"result": result}


@app.get("/materials/{query}")
async def get_on_materials(query: str = Path(...)):
    response = RedirectResponse('/')
    if is_task_id(query):
        response = RedirectResponse("/materials/task_id/".format(query))
    elif is_chemsys(query):
        response = RedirectResponse("/materials/chemsys/".format(query))
    elif is_formula(query):
        response = RedirectResponse("/materials/formula/".format(query))

    return response


def is_task_id(query):
    return False

def is_chemsys(query):
    return False

def is_formula(query):
    return False
