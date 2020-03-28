from maggma.stores import MongoStore  # type: ignore
from drone import Document, Drone




class MongoDrone(Drone):
    def __init__(self, store: MongoStore, key:str):
        self.store = store
        self.key = key

    def computeRecordIdentifierKey(self, document: Document) -> str:
        prefix, postfix = document.name.split(sep="-", maxsplit=1)
        ID, ftype = postfix.split(sep=".", maxsplit=1)
        return ID


