from drone import Drone, RecordIdentifier, Document
from typing import Dict, List, Union
from pathlib import Path
import os
from datetime import datetime
import re


class SimpleBibDrone(Drone):
    def __init__(self,
                 store, logger):
        super().__init__(store=store, logger=logger)

    def computeRecordIdentifier(self, record_key: str, doc_list: List[Document]) -> RecordIdentifier:
        """
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
        """
        Generate documents by going over the current directory:
        Note: Assumes that there's no folder in the current directory
        :param folder_path:
        :return:
        """
        files_paths = [folder_path / f for f in os.listdir(folder_path.as_posix())]
        return [Document(path=fp,
                         name=fp.name,
                         is_dir=Path.is_dir(fp)) for fp in files_paths]

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
        """
        Compute the recordIdentifier key by interpreting the name
        :param doc:
        :return:
        """
        prefix, postfix = doc.name.split(sep="-", maxsplit=1)
        ID, ftype = postfix.split(sep=".", maxsplit=1)
        return ID

    def organizeDocuments(self, documents: List[Document]) -> Dict[str, List[Document]]:
        """
        a dictionary that maps RecordIdentifierKey -> [File Paths]
            ex:
            1 -> [cite.bibtex(Represented in Document), data.txt(Represented in Document)]
            2 -> [cite2.bibtex(Represented in Document), text-2.txt(Represented in Document)]
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

class ComplexBibDrone(SimpleBibDrone):
    def __init__(self, store, logger):
        super().__init__(store=store, logger=logger)

    def computeRecordIdentifierKey(self, doc: Document) -> str:
        """
        THIS IS SHADY.

        I am assuming that there is always a  component in doc.path following the syntax 'citations-XXX' where XXX is
        the key. And citations-XXX is followed immediately either by a "/" or a "."

        I am also assuming that in the file path, the format citations-XXX appears first.
        look at the maxsplit=1 in split function

        :param doc: Document used to parse its id
        :return:
            The key for the record Identifier
        """
        pre, post = doc.path.as_posix().split("citations-", maxsplit=1)
        delimiters = ".", "/"
        regex_pattern = '|'.join(map(re.escape, delimiters))
        result = re.split(regex_pattern, post)
        key = result[0]
        return key

    def generateDocuments(self, folder_path: Path) -> List[Document]:
        result: List[Document] = []
        for path, dirs, files in os.walk(folder_path.as_posix()):
            for f in files:
                full_path = Path(path) / f
                doc = Document(path=full_path, name=full_path.name, is_dir=False)
                result.append(doc)
        return result

    def read(self, path: Path) -> List[RecordIdentifier]:
        documents = self.generateDocuments(path)
        mapping = self.organizeDocuments(documents)
        record_identifiers: List[RecordIdentifier] = [self.computeRecordIdentifier(key, docs)
                                                      for key, docs in mapping.items()]
        return record_identifiers

    def computeData(self, recordID: RecordIdentifier) -> Dict:
        return super().computeData(recordID)

    def organizeDocuments(self, documents: List[Document]) -> Dict[str, List[Document]]:
        """
        Organize the documents
        :param documents:
        :return:
        """
        return super().organizeDocuments(documents)


"""
3 -> citations-3.bibtex
1 -> cite.bibtex, data.txt
2 -> cite2.bibtex
"""