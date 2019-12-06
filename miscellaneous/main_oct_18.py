from examples.models import *
from fastapi import Path
from starlette.responses import RedirectResponse
from pymatgen.core.composition import Composition
from maggma.stores import JSONStore
from fastapi import FastAPI
from pymatgen.core.periodic_table import DummySpecie

app = FastAPI()
store = JSONStore("./data/more_mats.json")
store.connect()


@app.get("/")
async def root():
    collect = store.query()
    return {"result": "root"}


@app.get("/materials/task_id/{task_id}")
async def get_on_task_id(task_id: str = Path(..., title="The task_id of the item to get")):
    cursor = store.query(criteria={"task_id": task_id})
    return {"result": cursor[0]}


@app.get(
    "/materials/chemsys/{chemsys}",
    response_description="Get all the materials that matches the chemsys field",
    response_model=List[Material]
)
async def get_on_chemsys(chemsys: str = Path(..., title="The task_id of the item to get")):
    cursor = None
    elements = chemsys.split("-")
    unique_elements = set(elements) - {"*"}
    crit = dict()
    crit["elements"] = {"$all": list(unique_elements)}
    crit["nelements"] = len(elements)
    cursor = store.query(criteria=crit)
    raw_result = [c for c in cursor]
    for r in raw_result:
        material = Material(**r)
    return raw_result


@app.get(
    "/materials/formula/{formula}",
    response_model=List[Material],
    response_description="Get all the materials that matches the formula field"
)
async def get_on_formula(formula: str = Path(..., title="The formula of the item to get")):
    cursor = None
    if "*" in formula:
        nstars = formula.count("*")
        dummies = 'ADEGJLMQRXZ'
        formula_dummies = formula.replace("*", "{}").format(*dummies[:nstars])
        try:
            comp = Composition(formula_dummies).reduced_composition
            crit = dict()
            crit["formula_anonymous"] = comp.anonymized_formula
            real_elts = [str(e) for e in comp.elements
                         if not isinstance(e, DummySpecie)]
            # Paranoia below about floating-point "equality"
            crit.update(
                {'composition_reduced.{}'.format(el): {
                    "$gt": .99 * n, "$lt": 1.01 * n}
                    for el, n in comp.to_reduced_dict.items()
                    if el in real_elts})
            pretty_formula = comp.reduced_formula
            cursor = store.query(criteria=crit)
            result = [c for c in cursor]
            return result
        except Exception as e:
            raise e
    else:
        cursor = store.query(criteria={"formula_pretty": formula})
        return [] if cursor is None else [i for i in cursor]


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


# @app.put("/items/{item_id}")
# def update_item(id: int, material: Material):
#     return {"chemsys": material.chemsys, "task_id": material.task_id}


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
