from starlette.testclient import TestClient
from maggma.stores import JSONStore
from .routers.example_material.example_endpoint_cluster import EndpointCluster
from .routers.example_material.example_models import Material
from fastapi import FastAPI



class TestClass:
    store = JSONStore("../data/more_mats.json")
    store.connect()
    cluster = EndpointCluster(store, Material)

    app = FastAPI()
    app.include_router(
        cluster.router,
        prefix="/materials",
        responses={404: {"description": "Not found"}},
    )

    client = TestClient(app)

    def test_materials_root(self):
        response = self.client.get("/materials")
        assert response.status_code == 200
        assert response.json() == {"result": "At example root level"}

    def test_materials_task_id(self):
        task_id = "mp-7283"
        response = self.client.get("/materials/task_id/" + task_id)
        response_json = response.json()

        actual_json = self.store.query_one(criteria={"task_id": task_id})

        assert response.status_code == 200
        # assert response_json == actual_json
        assert response_json["chemsys"] == actual_json["chemsys"]
        assert response_json["density"] == actual_json["density"]

    def test_materials_get_on_chemsys(self):
        chemsys = "B-La"
        response = self.client.get("/materials/chemsys/" + chemsys)
        actual_cursor = self.store.query(criteria={"chemsys": chemsys})
        response_json = response.json()
        assert response.status_code == 200
        assert len(response_json) == actual_cursor.count()


