from maggma.stores import MongoStore
from BibDrone import *
from pathlib import Path
key = "record_key"
mongo_store = MongoStore(database="drone_test", collection_name="drone_test", key=key)
mongo_store.connect()
# simpleBibDrone = SimpleBibDrone(mongo_store, record_key=key)
# simpleBibDrone.assimilate(Path.cwd() / "data" / "example1", debug=True)

complexBibDrone = ComplexBibDrone(mongo_store, record_key=key)
complexBibDrone.assimilate(Path.cwd() / "data" / "example2", debug=True)
# complexBibDrone.printDirectory(Path.cwd() / "data" / "example2")
mongo_store.close()
