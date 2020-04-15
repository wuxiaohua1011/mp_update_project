from pathlib import Path
from typing import List, Iterable, Dict
import os
from drone import Drone, RecordIdentifier, Document
from maggma.core import Builder
from datetime import datetime


class SimpleBuilderDrone(Drone, Builder):
    """
    A Simple Drone that integrates Builder to
    1. read local files
    2. query database for similar files (Builder?)
    3. check whether database files needs to be updated
    4. update the database file if needed
    5. Do the above with multi-threading(Builder's job)
    """

    def __init__(self, store, path: Path):
        """

        :param store: The database to query
        :param path: local file path to scan
        """
        Drone.__init__(self, store)  # So why does Drone need to take care of store?
        Builder.__init__(self, sources=store, targets=store)
        # TODO: PROBLEM: Builder has self.logger, Drone also has self.logger
        # With current order, I think self.logger will be overwritten by
        # Builder's self.logger

        # TODO: Also, why does Drone also keep a store, since Builder should be the one solely responsible for the
        # interaction with the database
        self.path = path

    """
    Inherited methods
    """

    def compute_record_identifier_key(self, doc: Document) -> str:
        """
        THIS IS AN INHERITED METHOD
        Compute the recordIdentifier key by interpreting the name
        :param doc: gaurenteed to be a file
        :return:
        """
        prefix, postfix = doc.name.split(sep="-", maxsplit=1)
        ID, ftype = postfix.split(sep=".", maxsplit=1)
        return ID

    def read(self, path: Path) -> List[RecordIdentifier]:
        """
        THIS IS AN INHERITED METHOD
        Read from path and output a list of recordIDs where correlated citations and txt are grouped

        :param path: local file path to read
        :return:
            List of RecordIdentifiers
        """
        documents: List[Document] = self.generate_documents(folder_path=path)
        log = self.organize_documents(documents=documents)
        record_identifiers = [self.compute_record_identifier(record_key, doc_list)
                              for record_key, doc_list in log.items()]
        return record_identifiers

    def compute_data(self, recordID: RecordIdentifier) -> Dict:
        """
        THIS IS AN INHERITED METHOD
        Computes the data to upload by extracting the acutal content of the citation and its corresponding text
        :param recordID: recordID representing an association of citation and text file
        :return:
            A dictionary representing the data correspond to this recordID
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

    def get_items(self) -> Iterable:
        """
        THIS IS AN INHERITED METHOD
        This method will
        1. Read from local file path (self.path)
        2. query the database and ask for a list of items to return
        :return:
            And iterable with each item representing an item to update
        """
        self.logger.info("Starting get_items in {} Builder".format(self.__class__.__name__))
        record_identifiers: List[RecordIdentifier] = self.read(path=self.path)
        # So should we do database query natively in this method?
        records_to_update = self.should_update_records(record_identifiers)
        return records_to_update

    def process_item(self, item: Any) -> Any:
        pass

    def update_targets(self, items: List):
        """
        THIS IS AN INHERITED METHOD
        This method will:
        1. Convert a list of items into data to upload
        2. upload into the database

        :param items: list of items to convert into data, can also include meta data
        :return:
            None`
        """
        self.logger.info("Starting update in {} Builder".format(self.__class__.__name__))
        batched_data = [{**self.compute_data(recordID=record_identifier), **record_identifier.dict()}
                        for record_identifier in items]
        if len(batched_data) > 0:
            self.logger.info("Updating {} items".format(len(batched_data)))
            self.store.update(batched_data)
        else:
            self.logger.info("There are no items to update")

    """
    Helper Methods
    """

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

    def compute_record_identifier(self, record_key: str, doc_list: List[Document]) -> RecordIdentifier:
        """
        Compute meta data for this list of documents, and generate a RecordIdentifier object
        :param record_key: record keys that indicate a record
        :param doc_list: document on disk that this record include
        :return:
            RecordIdentifier that represent this doc_list
        """
        record_identifier = RecordIdentifier(last_updated=datetime.now(),
                                             documents=doc_list,
                                             record_key=record_key)
        record_identifier.state_hash = record_identifier.computeStateHashes()
        return record_identifier
