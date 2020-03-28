import hashlib
from os import listdir
from os.path import isfile, join
from pathlib import Path
import os
from typing import List, Dict, Union
from datetime import datetime

from maggma.stores import MongoStore  # type: ignore
from pydantic import BaseModel, Field
from pathlib import Path, PosixPath
from drone import Document, Drone, RecordIdentifier




class MongoDrone(Drone):
    def __init__(self, store: MongoStore, key:str):
        self.store = store
        self.key = key

    def computeRecordIdentifierKey(self, document: Document) -> str:
        prefix, postfix = document.name.split(sep="-", maxsplit=1)
        ID, ftype = postfix.split(sep=".", maxsplit=1)
        return ID







if __name__ == "__main__":
    key = "recordKey"
    mongo_store = MongoStore(database="drone_test", collection_name="drone_test", key=key)
    mongo_store.connect()

    mongoDrone = MongoDrone(mongo_store, key=key)

    mongoDrone.buildRecords(Path.cwd() / "data" / "folder1", debug=True)

    mongo_store.close()
