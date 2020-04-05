from drone import Drone, RecordIdentifier, Document
from typing import Dict, List
from pathlib import Path
import os
from datetime import datetime


class BibTexDrone(Drone):
    def __init__(self,
                 store,
                 record_key):
        super().__init__(store=store, record_key=record_key)

    def computeRecordIdentifier(self, record_key: str, doc_list: List[Document]) -> RecordIdentifier:
        """
        THIS SHOULD BE IN THE SPECIFIC DRONE
        Compute meta data for this list of documents, and generate a RecordIdentifier object
        :param record_key: record keys that indicate a record
        :param doc_list: document on disk that this record include
        :return:
            RecordIdentifier that represent this doc_list
        """
        recordIdentifier = RecordIdentifier(last_updated=datetime.now(),
                                            documents=doc_list,
                                            record_key=record_key)
        recordIdentifier.state_hash = recordIdentifier.computeStateHashes()
        return recordIdentifier

    def generateDocuments(self, folder_path: Path) -> List[Document]:
        files_paths = [folder_path / f for f in os.listdir(folder_path.as_posix())]
        return [Document(path=fp, name=fp.name) for fp in files_paths]

    def read(self, path: Path) -> List[RecordIdentifier]:
        """
        Given a folder path to a data folder, read all the files, and return a dictionary
        that maps each RecordKey -> [File Paths]

        ** Note: require user to implement the function computeRecordIdentifierKey

        :param path: Path object that indicate a path to a data folder
        :return:

        """
        documents: List[Document] = self.generateDocuments(folder_path=path)
        log = self.organizeDocuments(documents=documents)
        record_identifiers = [self.computeRecordIdentifier(record_key, doc_list)
                              for record_key, doc_list in log.items()]
        return record_identifiers

    def computeData(self, recordID: RecordIdentifier) -> Dict:
        """
        erturn the mapping of NAME_OF_DATA -> DATA

        :param recordID: recordID that needs to be re-saved
        :return:
            Dictionary of NAME_OF_DATA -> DATA
            ex:
                for a recordID refering to 1,
                {
                    "citation": cite.bibtex ,
                    "text": data.txt
                }
        """
        record = dict()

        for document in recordID.documents:
            if "citations" in document.name:
                with open(document.path.as_posix(), 'r') as file:
                    s = file.read()
                    record["citations"] = s

            if "text" in document.name:
                with open(document.path.as_posix(), 'r') as file:
                    s = file.read()
                    record["text"] = s
        return record

    def computeRecordIdentifierKey(self, doc: Document) -> str:
        prefix, postfix = doc.name.split(sep="-", maxsplit=1)
        ID, ftype = postfix.split(sep=".", maxsplit=1)
        return ID

    def organizeDocuments(self, documents: List[Document]) -> Dict[str, List[Document]]:
        """
        a dictionary that maps RecordIdentifierKey -> [File Paths]
            ex:
            1 -> [cite.bibtex(Represented in Document), data.txt(Represented in Document)]
            2 -> [citations-2.bibtex(Represented in Document), text-2.txt(Represented in Document)]
            3 -> [citations-3.bibtex(Represented in Document), ]
            ...
        :param documents:
        :return:
        """
        log = dict()
        for doc in documents:
            key = self.computeRecordIdentifierKey(doc)
            log[key] = log.get(key, []) + [doc]
        return log

