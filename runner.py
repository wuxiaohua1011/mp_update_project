from maggma.stores import MongoStore
from MongoDrone import MongoDrone
from pathlib import Path
key = "recordKey"
mongo_store = MongoStore(database="drone_test", collection_name="drone_test", key=key)
mongo_store.connect()

mongoDrone = MongoDrone(mongo_store, key=key)

mongoDrone.buildRecords(Path.cwd() / "data" / "folder1", debug=True, method=2)

mongo_store.close()
