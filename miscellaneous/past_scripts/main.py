from monty.io import zopen
import json
from fastapi import Path
from starlette.responses import RedirectResponse
from pymatgen.core.composition import Composition


with zopen("data/more_mats.json") as f:
    # data = f.read()
    parsed = json.load(f)


# parsed = loadfn("data/material_docs.json")
# parsed = jsanitize(parsed, allow_bson=True)
# print(parsed[1])
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
        if input_chemsys_elements == material_chemsys:
            result.append(material)
    return {"result": result}


@app.get("/materials/formula/{formula}")
async def get_on_formula(formula: str = Path(..., title="The formula of the item to get")):
    result = []
    user_composition = Composition(formula)
    for material in parsed:
        current_composition = Composition(material.get("formula_pretty"))
        if current_composition == user_composition:
            result.append(material)

    return {"result": result}


@app.get("/materials/{query}")
async def get_on_materials(query: str = Path(...)):
    if is_task_id(query):
        return RedirectResponse("/materials/task_id/{}".format(query))
    elif is_formula(query):
        return RedirectResponse("/materials/formula/{}".format(query))
    elif is_chemsys(query):
        return RedirectResponse("/materials/chemsys/{}".format(query))
    else:
        print("WARNING: Query <{}> does not match any of the endpoint features, returning to home".format(query))
        return RedirectResponse('/')


def is_task_id(query):
    if "-" in query:
        splits = query.split("-")
        if len(splits) == 2 and splits[1].isdigit():
            return True
    return False


def is_formula(query):
    try:
        c = Composition(query)
        return True
    except:
        return False


def is_chemsys(query):
    return True ## TODO split on dash, Composition(query),
