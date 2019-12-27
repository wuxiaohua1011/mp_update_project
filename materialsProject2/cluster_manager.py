from fastapi import FastAPI
from endpoint_cluster import EndpointCluster
from maggma.stores import JSONStore
from models import MaterialModel, SpecieModel
from materials_endpoint import MaterialEndpointCluster
import uvicorn
from monty.json import MSONable


class ClusterManager(MSONable):
    def __init__(self):
        self.endpoints = dict()
        self.app = FastAPI()

    def addEndpoint(self, endpoint: EndpointCluster):
        """
        add a endpoint to the cluster manager
        Args:
            endpoint: the new endpoint to add in

        Returns:
            None
        """
        assert endpoint.prefix not in self.endpoints, "ERR: endpoint [{}] already exist, please modify the endpoint " \
                                                      "in-place".format(endpoint.prefix)

        self.endpoints[endpoint.prefix] = endpoint

    def runAllEndpoints(self):
        """
        Must of AT LEAST one endpoint in the list
        initialize and run all endpoints with their respective parameters

        Returns:
            None
        """
        assert len(self.endpoints) > 0, "ERROR: There are no endpoints provided"
        # print(self.endpoints)
        for prefix, endpoint in self.endpoints.items():
            self.app.include_router(
                endpoint.router,
                prefix=prefix
            )
        uvicorn.run(self.app, host="127.0.0.1", port=8000, log_level="info", reload=False)

    def getEndpoints(self):
        """

        Returns:
            a list of existing endpoints
        """
        return self.endpoints.values()

    # things needed
    # tags
    # look at bigger application in fastapi
    # responses (cluster manager can override endpoints'), and application.py
    # Make Google Docstrings


#############################################
####### TESTING CODE FOR THIS FILE ##########
#############################################
if __name__ == "__main__":
    json_store = JSONStore("../data/more_mats.json")
    json_store.connect()

    ## initialize endpoints
    mp_endpoint1 = MaterialEndpointCluster(db_source=json_store, prefix="/materials1", tags=["material", "1"])
    mp_endpoint2 = MaterialEndpointCluster(db_source=json_store, prefix="/materials2", tags=["material", "2"])
    general_endpoint = EndpointCluster(db_source=json_store, model=SpecieModel)

    clusterManager = ClusterManager()
    clusterManager.addEndpoint(mp_endpoint1)
    clusterManager.addEndpoint(mp_endpoint2)
    clusterManager.addEndpoint(general_endpoint)

    clusterManager.runAllEndpoints()
