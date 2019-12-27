from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi import Path

from models import Material, CommonPaginationParams
from pymatgen.core.composition import Composition, CompositionError
from pymatgen.core.periodic_table import DummySpecie
from typing import List
from starlette.responses import RedirectResponse
from monty.json import MSONable

import uvicorn

class EndpointCluster(MSONable):
    def __init__(self, db_source, model, prefix: str = "", tags : list = []):
        self.db_source = db_source
        self.router = APIRouter()
        # self.app = app # no need, include router in manager
        self.prefix = prefix
        self.model = model
        self.tags = tags

        self.router.post("/simple_post")(self.simple_post)
        self.router.get("/", tags=self.tags)(self.root)
        # self.prepareEndpoint()

    async def root(self):
        """
        Default root response

        Returns:
            Default response
        """
        return {"response": "At root level"}

    async def simple_post(self, data: str):
        # https://www.errietta.me/blog/python-fastapi-intro/
        # https://fastapi.tiangolo.com/tutorial/request-forms/
        return {"response": "posting " + data}

    @property
    def app(self):
        app = FastAPI()
        app.include_router(
            self.router,
            prefix="")
        # NOTE: per documentation of uvicorn, unable to attach reload=True attribute
        # https://www.uvicorn.org/deployment/#running-programmatically
        return app

    # def run(self, prefix=""):
    #     """
    #     Deploy single endpoint as an INDIVIDUAL and SEPARATE app
    #
    #     """
    #     # app = FastAPI()
    #     # app.include_router(
    #     #     self.router,
    #     #     prefix=prefix)
    #     # NOTE: per documentation of uvicorn, unable to attach reload=True attribute
    #     # https://www.uvicorn.org/deployment/#running-programmatically
    #     uvicorn.run(self.app, host="127.0.0.1", port=8000, log_level="info", reload=False)

