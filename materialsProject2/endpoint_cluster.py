from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi import Path

from models import Material, CommonPaginationParams
from pymatgen.core.composition import Composition, CompositionError
from pymatgen.core.periodic_table import DummySpecie
from typing import List
from starlette.responses import RedirectResponse
from monty.json import MSONable
import pydantic

# CITATION: https://gist.github.com/bl4de/3086cf26081110383631
# Table mapping response codes to messages; entries have the
default_responses = {
    100: {"description": 'Continue'},
    101: {"description": 'Switching Protocols'},

    200: {"description": 'OK'},
    201: {"description": 'Created'},
    202: {"description": 'Accepted'},
    203: {"description": 'Non-Authoritative Information'},
    204: {"description": 'No Content'},
    205: {"description": 'Reset Content'},
    206: {"description": 'Partial Content'},

    300: {"description": 'Multiple Choices'},
    301: {"description": 'Moved Permanently'},
    302: {"description": 'Found'},
    303: {"description": 'See Other'},
    304: {"description": 'Not Modified'},
    305: {"description": 'Use Proxy'},
    307: {"description": 'Temporary Redirect'},

    400: {"description": 'Bad Request'},
    401: {"description": 'Unauthorized'},
    402: {"description": 'Payment Required'},
    403: {"description": 'Forbidden'},
    404: {"description": 'Not Found'},
    405: {"description": 'Method Not Allowed'},
    406: {"description": 'Not Acceptable'},
    407: {"description": 'Proxy Authentication Required'},
    408: {"description": 'Request Timeout'},
    409: {"description": 'Conflict'},
    410: {"description": 'Gone'},
    411: {"description": 'Length Required'},
    412: {"description": 'Precondition Failed'},
    413: {"description": 'Request Entity Too Large'},
    414: {"description": 'Request-URI Too Long'},
    415: {"description": 'Unsupported Media Type'},
    416: {"description": 'Requested Range Not Satisfiable'},
    417: {"description": 'Expectation Failed'},

    500: {"description": 'Internal Server Error'},
    501: {"description": 'Not Implemented'},
    502: {"description": 'Bad Gateway'},
    503: {"description": 'Service Unavailable'},
    504: {"description": 'Gateway Timeout'},
    505: {"description": 'HTTP Version Not Supported'}
}



class EndpointCluster(MSONable):
    def __init__(self, db_source, model: pydantic.BaseModel, prefix: str = "", tags: list = [], responses: dict = {}):
        self.db_source = db_source
        self.router = APIRouter()
        # self.app = app # no need, include router in manager
        self.prefix = prefix
        self.model = model
        self.tags = tags
        self.responses = default_responses.copy()

        self.responses.update(responses)

        self.router.post("/simple_post")(self.simple_post)
        self.router.get("/",
                        tags=self.tags,
                        responses=self.responses)(self.root)
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
