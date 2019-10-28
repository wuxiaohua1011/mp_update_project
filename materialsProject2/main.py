from fastapi import FastAPI
from maggma.stores import JSONStore
from routers.example_material.Endpoint import Endpoint
from routers.example_material.example_models import Material

store = JSONStore("../data/more_mats.json")
store.connect()
endpoint = Endpoint(store, Material)

app = FastAPI()

app.include_router(
    endpoint.router,
    prefix="/materials",
    responses={404: {"description": "Not found"}},
)


