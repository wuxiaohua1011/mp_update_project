# import testing modules

# set module path
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# import files
from models import MaterialModel
from fastapi import HTTPException, Depends
from fastapi import Path

from models import CommonPaginationParams
from pymatgen.core.composition import Composition, CompositionError
from typing import List
from starlette.responses import RedirectResponse
from endpoint_cluster import EndpointCluster
from maggma.stores import JSONStore
from starlette.responses import JSONResponse
import uvicorn
import starlette.status


class MaterialEndpointCluster(EndpointCluster):
    def __init__(self, db_source: JSONStore, tags=[], responses={}, prefix: str = "/materials"):
        super().__init__(db_source, MaterialModel, prefix, tags, responses)
        # initialize routes
        # self.model = MaterialModel in this case

        self.router.get("/task_id/{task_id}",
                        response_description="Get Task ID",
                        response_model=self.model,
                        tags=self.tags,
                        responses=self.responses
                        ) \
            (self.get_on_task_id)
        self.router.get("/chemsys/{chemsys}",
                        response_description="Get all the materials that matches the chemsys field",
                        response_model=List[self.model],
                        tags=self.tags,
                        responses=self.responses
                        )(self.get_on_chemsys)
        self.router.get("/formula/{formula}",
                        response_model=List[self.model],
                        response_description="Get all the materials that matches the formula field",
                        tags=self.tags,
                        responses=self.responses) \
            (self.get_on_formula)
        self.router.get("/{query}",
                        tags=self.tags,
                        responses=self.responses)(self.get_on_materials)
        self.router.get("/distinct/",
                        tags=self.tags,
                        responses= self.responses)(self.get_distinct_choices)

    async def get_on_chemsys(self, chemsys: str = Path(..., title="The task_id of the item to get"),
                             paginationParam: CommonPaginationParams = Depends()):
        """
        Ex: http://127.0.0.1:8000/chemsys/B-La
        Args:
            chemsys: the user input of chemical system
            paginationParam: optional skip and limit parameter

        Returns:
            list of materials that satisfy the input chemsys, limited by the paginationParam
        """
        skip, limit = paginationParam.skip, paginationParam.limit
        cursor = None
        elements = chemsys.split("-")
        unique_elements = set(elements) - {"*"}
        crit = dict()
        crit["elements"] = {"$all": list(unique_elements)}
        crit["nelements"] = len(elements)
        cursor = self.db_source.query(criteria=crit)
        raw_result = [c for c in cursor]
        for r in raw_result:
            material = MaterialModel(**r)
        if len(raw_result) == 0:
            return JSONResponse(status_code=404, content=self.responses[404])
        return raw_result[skip:skip+limit]

    async def get_on_formula(self, formula: str = Path(..., title="The formula of the item to get"),
                             paginationParam: CommonPaginationParams = Depends()):
        """
        Return the materials that matches the input formula
        - **formula**: The formula of the item to get
        - **paginationParam**:

        Ex: http://127.0.0.1:8000/formula/LaB4
        Args:
            formula: the user input of formula anonymous
            paginationParam: optional skip and limit parameter

        Returns:
            list of materials that satisfy the user input formula, limited by the paginationParam
        """
        skip, limit = paginationParam.skip, paginationParam.limit
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
                             if not e.as_dict().get("element", "A") in dummies]

                # Paranoia below about floating-point "equality"
                for el, n in comp.to_reduced_dict.items():
                    if el in real_elts:
                        crit['composition_reduced.{}'.format(el)] = {"$gt": .99 * n, "$lt": 1.01 * n}

                # pretty_formula = comp.reduced_formula
                cursor = self.db_source.query(criteria=crit)
                result = [c for c in cursor]
                if len(result) == 0:
                    return JSONResponse(status_code=404, content=self.responses[404])
                return result[skip:skip + limit]
            except Exception as e:
                raise e
        else:
            cursor = self.db_source.query(criteria={"formula_pretty": formula})
            if cursor is None:
                return JSONResponse(status_code=404, content=self.responses[404])
            else:
                result = [] if cursor is None else [i for i in cursor]
                return result[skip:skip + limit]

    async def get_on_materials(self, query: str = Path(...)):
        """
        To re-route to the correct route
        Args:
            query: the input query, can be in any string format

        Returns:
            RedirectResponse to the correct route
        """
        if self.is_task_id(query):
            return RedirectResponse("/task_id/{}".format(query))
        elif self.is_chemsys(query):
            return RedirectResponse("/chemsys/{}".format(query))
        elif self.is_formula(query):
            return RedirectResponse("/formula/{}".format(query))
        else:
            return HTTPException(status_code=404,
                                 detail="WARNING: Query <{}> does not match any of the endpoint features".format(query))

    async def get_distinct_choices(self,
                                   paginationParam: CommonPaginationParams = Depends()):
        """

        Args:
            paginationParam:

        Returns:
            List of distint values of each field
        """
        skip, limit = paginationParam.skip, paginationParam.limit
        data = self.db_source.query_one()
        keys = data.keys()
        result = dict()
        for k in keys:
            result[k] = self.db_source.distinct(k)[skip:skip + limit]
        return result

    async def get_on_task_id(self, task_id: str = Path(..., title="The task_id of the item to get")):
        """
        http://127.0.0.1:8000/task_id/mp-30933
        Args:
            task_id: in the format of mp-NUMBER

        Returns:
            a single material that satisfy the Material Model
        """
        cursor = self.db_source.query(criteria={"task_id": task_id})
        material = cursor[0] if cursor.count() > 0 else None
        if material:
            material = self.model(**material)
            return material
        else:
            raise HTTPException(status_code=404, detail="Item with Task_id = {} not found".format(task_id))

    def is_chemsys(self, query: str):
        if "-" in query:
            query = query.split("-")
            for q in query:
                try:
                    Composition(q)
                except CompositionError as e:
                    return False
            return True
        return False

    def is_formula(self, query):
        try:
            Composition(query)
            return True
        except Exception:
            return False

    def is_task_id(self, query):
        if "-" in query:
            splits = query.split("-")
            if len(splits) == 2 and splits[1].isdigit():
                return True
        return False


#############################################
####### TESTING CODE FOR THIS FILE ##########
#############################################
# store = JSONStore("../data/more_mats.json")
# store.connect()
# materialEndpointCluster = MaterialEndpointCluster(store)
#
# # materialEndpointCluster.run()
# app = materialEndpointCluster.app
# if __name__ == "__main__":
#     uvicorn.run("materials_endpoint:app", host="127.0.0.1", port=8000, log_level="info", reload=False)
