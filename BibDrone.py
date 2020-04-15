from drone import Drone, RecordIdentifier, Document
from typing import Dict, List, Union
from pathlib import Path
import os
from datetime import datetime
import re


class SimpleBibDrone(Drone):
    def __init__(self,
                 store, path):
        super().__init__(store=store, path)

    def compute_record_identifier(self, record_key: str, doc_list: List[Document]) -> RecordIdentifier:
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

    def generate_documents(self, folder_path: Path) -> List[Document]:
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
        documents: List[Document] = self.generate_documents(folder_path=path)
        log = self.organize_documents(documents=documents)
        record_identifiers = [self.compute_record_identifier(record_key, doc_list)
                              for record_key, doc_list in log.items()]
        return record_identifiers

    def compute_data(self, recordID: RecordIdentifier) -> Dict:
        """
        return the mapping of NAME_OF_DATA -> DATA

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

    def compute_record_identifier_key(self, doc: Document) -> str:
        """
        Compute the recordIdentifier key by interpreting the name
        :param doc:
        :return:
        """
        prefix, postfix = doc.name.split(sep="-", maxsplit=1)
        ID, ftype = postfix.split(sep=".", maxsplit=1)
        return ID

    def organize_documents(self, documents: List[Document]) -> Dict[str, List[Document]]:
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
            key = self.compute_record_identifier_key(doc)
            log[key] = log.get(key, []) + [doc]
        return log

class ComplexBibDrone(SimpleBibDrone):
    def __init__(self, store, logger):
        super().__init__(store=store, logger=logger)

    def compute_record_identifier_key(self, doc: Document) -> str:
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

    def generate_documents(self, folder_path: Path) -> List[Document]:
        result: List[Document] = []
        for path, dirs, files in os.walk(folder_path.as_posix()):
            for f in files:
                full_path = Path(path) / f
                doc = Document(path=full_path, name=full_path.name, is_dir=False)
                result.append(doc)
        return result

    def read(self, path: Path) -> List[RecordIdentifier]:
        documents = self.generate_documents(path)
        mapping = self.organize_documents(documents)
        record_identifiers: List[RecordIdentifier] = [self.compute_record_identifier(key, docs)
                                                      for key, docs in mapping.items()]
        return record_identifiers

    def compute_data(self, recordID: RecordIdentifier) -> Dict:
        return super().compute_data(recordID)

    def organize_documents(self, documents: List[Document]) -> Dict[str, List[Document]]:
        """
        Organize the documents
        :param documents:
        :return:
        """
        return super().organize_documents(documents)


"""
3 -> citations-3.bibtex
1 -> cite.bibtex, data.txt
2 -> cite2.bibtex
"""