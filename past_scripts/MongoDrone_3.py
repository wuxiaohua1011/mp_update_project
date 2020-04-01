from typing import Dict

from maggma.stores import MongoStore  # type: ignore
from past_scripts.drone_3 import Document, Drone, RecordIdentifier


class BibtexDrone(Drone):
    """
    Read bibtext and store a key called citation,
    read txt, store it under a key called txt
    """
    def __init__(self, store: MongoStore, key:str):
        self.store = store
        self.key = key

    def computeRecordIdentifierKey(self, document: Document) -> str:
        prefix, postfix = document.name.split(sep="-", maxsplit=1)
        ID, ftype = postfix.split(sep=".", maxsplit=1)
        return ID

    def process(self, recordId: RecordIdentifier) -> Dict:
        record = dict()

        for name, doc in recordId.documents.items():
            if "citations" in name:
                with open(doc.path.as_posix(), 'r') as file:
                    s = file.read()
                    record["citations"] = s

            if "text" in name:
                with open(doc.path.as_posix(), 'r') as file:
                    s = file.read()
                    record["text"] = s
        # {"citation": balbah, "text": alajdf}
        return record


