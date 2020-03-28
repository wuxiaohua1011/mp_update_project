from pydantic import BaseModel, Field
from pathlib import PosixPath, Path
from datetime import datetime
from typing import Dict, List, Union
from monty.json import MSONable
from maggma.core import Store
import os
import hashlib
from abc import ABCMeta, abstractmethod

class Document(BaseModel):
    path: PosixPath = Field(..., title="Path of this file")
    name: str = Field(..., title="File name")
    md5sum: str = Field(..., title="md5 hash of the state of the file")


class RecordIdentifier(BaseModel):
    last_updated: datetime = Field(..., title="The time in which this record is last updated")
    documents: Dict[str, Document] = Field(..., title="Dictionary representing the document name to its corresponding "
                                                      "document")
    recordKey: str = Field(...,
                           title="Hash that uniquely define this record, can be inferred from each document inside")
    # stateHash: str = Field(..., title="Hash of the state of the documents in this Record")

class Drone(MSONable):
    def __init__(self, store: Store, key: str):
        self.store = store
        self.key = key

    def getRecordIdentifier(self, document: Document) -> RecordIdentifier:
        key = self.computeRecordIdentifierKey(document)
        record = self.store.query_one(criteria={self.key: key})
        if record is None:
            return self.createRecordIdentifier(document=document)
        else:
            return record

    def buildRecords(self, documents: Union[List[BaseModel], Path], debug=False):
        if isinstance(documents, Path):
            documents = self.generateDocuments(documents)

        for doc in documents:
            r = self.getRecordIdentifier(document=doc)
            status = self.updateRecordIdentifier(r, doc)
            if debug:
                print("Modified? {}, doc = {}, record = {}".format(status, doc.name, r.recordKey))
                print()

    def generateDocuments(self, folder_path: Path) -> List[Document]:
        files_paths = [folder_path / f for f in os.listdir(folder_path.as_posix())]
        return [self.createDocument(fp) for fp in files_paths]

    def createDocument(self, path: Path) -> Document:
        with open(path.as_posix(), 'rb') as file:
            s = file.read()
        md5sum = hashlib.md5(s).hexdigest()
        return Document(path=path, name=path.name, md5sum=md5sum)

    def updateRecordIdentifier(self, recordIdentifier: RecordIdentifier, document: Document) -> bool:
        """
        Guaranteed recordIdentifier is not null and that this record needs update
        :param recordIdentifier:
        :param document:
        :return:
        """
        modified = False
        if document.name in recordIdentifier.documents.keys():
            if document.md5sum != recordIdentifier.documents[document.name].md5sum:
                recordIdentifier.documents[document.name] = document
                modified = True
        else:
            recordIdentifier.documents[document.name] = document
            modified = True

        if modified:
            recordIdentifier.last_updated = datetime.now()
            # recordIdentifier.stateHash = hashlib.md5(recordIdentifier.documents)
            return True
        return False

    def createRecordIdentifier(self, document: Document) -> RecordIdentifier:
        documents = {document.name: document}
        # stateHash = hash(documents)
        return RecordIdentifier(last_updated=datetime.now(),
                                documents=documents,
                                recordKey=self.computeRecordIdentifierKey(document))

    @abstractmethod
    def computeRecordIdentifierKey(self, document: Document) -> str:
        raise NotImplementedError