from maggma.stores import MongoStore
from BibDrone import BibTexDrone
from pathlib import Path
key = "record_key"
mongo_store = MongoStore(database="drone_test", collection_name="drone_test", key=key)
mongo_store.connect()

bibDrone = BibTexDrone(mongo_store, record_key=key)

bibDrone.assimilate(Path.cwd() / "data" / "folder1", debug=True)

mongo_store.close()
