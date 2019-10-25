from fastapi import FastAPI
from maggma.stores import JSONStore
from routers.example_material.Endpoint import Endpoint

store = JSONStore("../data/more_mats.json")
store.connect()
endpoint = Endpoint(store)

app = FastAPI()

app.include_router(
    endpoint.router,
    prefix="/materials",
    responses={404: {"description": "Not found"}},
)


