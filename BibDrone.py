from drone import Drone, RecordIdentifier, Document
from typing import Dict, List
from pathlib import Path
import os


class BibTexDrone(Drone):
    def __init__(self,
                 store,
                 record_key):
        super().__init__(store=store, record_key=record_key)

    def computeData(self, recordID: RecordIdentifier) -> Dict:
        """
        erturn the mapping of NAME_OF_DATA -> DATA

        :param recordID: recordID that needs to be re-saved
        :return:
            Dictionary of NAME_OF_DATA -> DATA
            ex:
                for a recordID refering to 1,
                {
                    "citation": citations-1.bibtex ,
                    "text": text-1.txt
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

    def generateDocuments(self, folder_path: Path) -> List[Document]:
        files_paths = [folder_path / f for f in os.listdir(folder_path.as_posix())]
        return [Document(path=fp, name=fp.name) for fp in files_paths]

    def computeRecordIdentifierKey(self, doc: Document) -> str:
        prefix, postfix = doc.name.split(sep="-", maxsplit=1)
        ID, ftype = postfix.split(sep=".", maxsplit=1)
        return ID