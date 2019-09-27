from models import *
from fastapi import Path
from starlette.responses import RedirectResponse, Response
from pymatgen.core.composition import Composition
from maggma.stores import JSONStore
from fastapi import FastAPI


app = FastAPI()
store = JSONStore("./data/more_mats.json")
store.connect()


@app.get("/")
async def root():
    collect = store.query()
    return {"message": str(collect[0])}


@app.get("/materials/task_id/{task_id}")
async def get_on_task_id(task_id: str = Path(..., title="The task_id of the item to get")):
    cursor = store.query(criteria={"task_id": task_id})
    return {"result": cursor[0]}


@app.get("/materials/chemsys/{chemsys}")
async def get_on_chemsys(chemsys: str = Path(..., title="The task_id of the item to get")):
    raise Exception("NOT IMPLEMENTED")
    result = []
    # input_chemsys_elements = set(chemsys.split("-"))
    #
    # for material in parsed:
    #     material_chemsys = set(material.get("chemsys").split("-"))
    #     if input_chemsys_elements == material_chemsys:
    #         result.append(material)
    return {"result": result}


@app.get("/materials/formula/{formula}")
async def get_on_formula(formula: str = Path(..., title="The formula of the item to get")):
    raise Exception("NOT IMPLEMENTED")
    result = []
    # user_composition = Composition(formula)
    # for material in parsed:
    #     current_composition = Composition(material.get("formula_pretty"))
    #     if current_composition == user_composition:
    #         result.append(material)

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


@app.put("/items/{item_id}")
def update_item(id: int, material: Material):
    return {"chemsys": material.chemsys, "task_id": material.task_id}


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
    return True  ## TODO split on dash, Composition(query),
