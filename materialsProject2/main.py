from maggma.stores import JSONStore
from routers.example_material.Endpoint import Endpoint
from routers.example_material.example_models import Material

store = JSONStore("../data/more_mats.json")
store.connect()
endpoint = Endpoint(store, Material)

endpoint.run()
