from maggma.stores import JSONStore # THIS IS ALREADY maggma
from routers.example_material.example_endpoint_cluster import EndpointCluster
from routers.example_material.example_models import Material

store = JSONStore("../data/more_mats.json")
store.connect()
materialEndpointCluster = EndpointCluster(store, Material)

materialEndpointCluster.run()

