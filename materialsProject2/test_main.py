from starlette.testclient import TestClient
from maggma.stores import JSONStore
from .routers.example_material.Endpoint import Endpoint
from .routers.example_material.example_models import Material
from fastapi import FastAPI

store = JSONStore("../data/more_mats.json")
store.connect()
endpoint = Endpoint(store, Material)

app = FastAPI()

app.include_router(
    endpoint.router,
    prefix="/materials",
    responses={404: {"description": "Not found"}},
)

client = TestClient(app)


def test_materials_root():
    response = client.get("/materials")
    assert response.status_code == 200
    assert response.json() == {"result": "At example root level"}

def test_materials_task_id():
    response = client.get("/materials/task_id/mp-29646")
    assert response.status_code == 200
    response_json = response.json()
    print(response_json) # TODO how to compare json...
