from maggma.stores import MongoStore
from BibDrone import SimpleBibDrone, ComplexBibDrone
from pathlib import Path
from builder_drone import SimpleBuilderDrone
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

key = "record_key"
mongo_store = MongoStore(database="drone_test", collection_name="drone_test", key=key)
# mongo_store.connect()
# simpleBibDrone = SimpleBibDrone(mongo_store, record_key=key)
# simpleBibDrone.assimilate(Path.cwd() / "data" / "example1", debug=True)

# complexBibDrone = ComplexBibDrone(mongo_store, logger=logger)
# complexBibDrone.assimilate(Path.cwd() / "data" / "example2")
# # complexBibDrone.printDirectory(Path.cwd() / "data" / "example2")
# mongo_store.close()

simple_path = Path.cwd() / "data" / "example1"
simple_builder_drone = SimpleBuilderDrone(store=mongo_store, path=simple_path)
simple_builder_drone.connect()

# The line below is essentially the function assimilate in Drone.py. So do we still need the assimilate function?
simple_builder_drone.update_targets(simple_builder_drone.get_items([process]))

simple_builder_drone.finalize()