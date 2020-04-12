from maggma.stores import MongoStore
from BibDrone import *
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

key = "record_key"
mongo_store = MongoStore(database="drone_test", collection_name="drone_test", key=key)
mongo_store.connect()
# simpleBibDrone = SimpleBibDrone(mongo_store, record_key=key)
# simpleBibDrone.assimilate(Path.cwd() / "data" / "example1", debug=True)

complexBibDrone = ComplexBibDrone(mongo_store, logger=logger)
complexBibDrone.assimilate(Path.cwd() / "data" / "example2")
# complexBibDrone.printDirectory(Path.cwd() / "data" / "example2")
mongo_store.close()
