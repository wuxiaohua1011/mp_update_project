from maggma.stores import JSONStore # THIS IS ALREADY maggma
from endpoint_cluster import EndpointCluster
from examples.models import Material

store = JSONStore("../data/more_mats.json")
store.connect()
materialEndpointCluster = EndpointCluster(store, Material)

materialEndpointCluster.run()

