from fastapi import APIRouter, HTTPException
from fastapi import Path
from .example_models import Material
from pymatgen.core.composition import Composition, CompositionError
from pymatgen.core.periodic_table import DummySpecie
from typing import List
from starlette.responses import RedirectResponse
from monty.json import MSONable


def is_chemsys(query: str):
    if "-" in query:
        query = query.split("-")
        for q in query:
            try:
                Composition(q)
            except CompositionError as e:
                return False
        return True
    return False


def is_formula(query):
    try:
        Composition(query)
        return True
    except CompositionError as e:
        return False


def is_task_id(query):
    if "-" in query:
        splits = query.split("-")
        if len(splits) == 2 and splits[1].isdigit():
            return True
    return False


class Endpoint(MSONable):
    def __init__(self, db_source, model):
        self.db_source = db_source
        self.router = APIRouter()
        self.Model = model

        self.router.get("/")(self.root)
        self.router.get("/{query}")(self.get_on_materials)
        self.router.get("/distinct/")(self.get_distinct_choices)

        # dynamic dispatch?
        if hasattr(self.Model, "__annotations__"):
            attr = self.Model.__dict__.get("__annotations__")
            if attr.get("task_id"):
                self.router.get("/task_id/{task_id}",
                                response_description="Get the material that matches the task id, should be only one "
                                                     "material",
                                response_model=self.Model) \
                    (self.get_on_task_id)

            if attr.get("chemsys"):
                self.router.get("/chemsys/{chemsys}",
                                response_description="Get all the materials that matches the chemsys field",
                                response_model=List[self.Model]) \
                    (self.get_on_chemsys)
            if attr.get("formula"):
                self.router.get("/formula/{formula}",
                                response_model=List[self.Model],
                                response_description="Get all the materials that matches the formula field") \
                    (self.get_on_formula)

    async def root(self):
        data = self.db_source.query_one()
        keys = data.keys()
        result = dict()
        for k in keys:
            result[k] = self.db_source.distinct(k)
        return {"result": "At example root level"}

    async def get_on_task_id(self, task_id: str = Path(..., title="The task_id of the item to get")):
        cursor = self.db_source.query(criteria={"task_id": task_id})
        material = cursor[0] if cursor.count() > 0 else None
        if material:
            material = self.Model(**material)
            return material
        else:
            raise HTTPException(status_code=404, detail="Item not found")

    async def get_on_chemsys(self, chemsys: str = Path(..., title="The task_id of the item to get"),
                             skip: int = 0,
                             limit: int = 10
                             ):
        cursor = None
        elements = chemsys.split("-")
        unique_elements = set(elements) - {"*"}
        crit = dict()
        crit["elements"] = {"$all": list(unique_elements)}
        crit["nelements"] = len(elements)
        cursor = self.db_source.query(criteria=crit)
        raw_result = [c for c in cursor]
        for r in raw_result:
            material = Material(**r)
        return raw_result[skip:skip + limit]

    async def get_on_formula(self, formula: str = Path(..., title="The formula of the item to get"),
                             skip: int = 0,
                             limit: int = 10
                             ):
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
                cursor = self.db_source.query(criteria=crit)
                result = [c for c in cursor]
                return result[skip:skip + limit]
            except Exception as e:
                raise e
        else:
            cursor = self.db_source.query(criteria={"formula_pretty": formula})
            result = [] if cursor is None else [i for i in cursor]
            return result[skip:skip + limit]

    async def get_on_materials(self, query: str = Path(...)):
        if is_task_id(query):
            return RedirectResponse("/materials/task_id/{}".format(query))
        elif is_formula(query):
            return RedirectResponse("/materials/formula/{}".format(query))
        elif is_chemsys(query):
            return RedirectResponse("/materials/chemsys/{}".format(query))
        else:
            return HTTPException(status_code=404,
                                 detail="WARNING: Query <{}> does not match any of the endpoint features".format(query))

    async def get_distinct_choices(self,
                                   skip: int = 0,
                                   limit: int = 10):
        data = self.db_source.query_one()
        keys = data.keys()
        result = dict()
        for k in keys:
            result[k] = self.db_source.distinct(k)[skip:skip + limit]
        return result
