from pydantic import BaseModel, Field
from pathlib import PosixPath, Path
from datetime import datetime
from typing import Dict, List, Optional, Iterable
from monty.json import MSONable
import hashlib
from abc import abstractmethod
import os.path
import logging
from maggma.core import Builder
from typing import Any
class Document(BaseModel):
    path: PosixPath = Field(..., title="Path of this file")
    name: str = Field(..., title="File name")
    is_dir: bool = False


class RecordIdentifier(BaseModel):
    """
    The meta data for a record
    """
    last_updated: datetime = Field(..., title="The time in which this record is last updated")
    documents: List[Document] = Field([], title="List of documents this RecordIdentifier indicate")
    record_key: str = Field(...,
                            title="Hash that uniquely define this record, can be inferred from each document inside")
    state_hash: Optional[str] = Field(None, title="Hash of the state of the documents in this Record")

    @property
    def parentDirectory(self) -> Path:
        """
        root most directory that documnents in this record share
        :return:
        """
        paths = [doc.path.as_posix() for doc in self.documents]
        return Path(os.path.commonprefix(paths))

    def computeStateHashes(self) -> str:
        """
        compute the hash of the state of the documents in this record
        :param doc_list: list of documents
        :return:
            hash of the list of documents passed in
        """
        digest = hashlib.md5()
        for doc in self.documents:
            digest.update(doc.name.encode())
            with open(doc.path.as_posix(), 'rb') as file:
                buf = file.read()
                digest.update(buf)
        return str(digest.hexdigest())


class Drone(Builder):
    """
    An abstract drone that handles operations with database
    User have to implement all abstract methods to specify the data that they want to use to interact with this class


    - Step 1(readRecord):
        - Crawl through Path of the folder where data live
            - it will return Record of  (Already in method 2)
                (cite.bibtex, data.txt)
                (cite2.bibtex, text-2.txt)
                (citations-3.bibtex, ) ...
     - Step 2: Takes a list of Record (from the result above), and say if it should be updated or not
        - If you've seen it before and the raw data has changed --> return True
        - If you never seen it before --> return True
        - Otherwise --> return False
     - Step 3: Process the Record (convert the Record into MongoDB data) (abstract function)
     - Step 4: Inject back the meta data to see if the Record if needed to be updated
     - Step 5: Inject into the data base
    """

    def __init__(self,store, path):
        self.store = store
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.addHandler(logging.NullHandler())
        self.path = path
        super().__init__(sources=[], targets=store)

    @abstractmethod
    def compute_record_identifier_key(self, doc: Document) -> str:
        """
        Compute the RecordIdentifier key that this document correspond to
        :param doc: document which the record identifier key will be inferred from
        :return:
            RecordIdentifiierKey
        """
        raise NotImplementedError

    @abstractmethod
    def read(self, path: Path) -> List[RecordIdentifier]:
        """
        Given a folder path to a data folder, read all the files, and return a dictionary
        that maps each RecordKey -> [File Paths]

        ** Note: require user to implement the function computeRecordIdentifierKey

        :param path: Path object that indicate a path to a data folder
        :return:

        """
        raise NotImplementedError

    @abstractmethod
    def compute_data(self, recordID: RecordIdentifier) -> Dict:
        """
        User can specify what raw data they want to save from the Documents that this recordID refers to

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
        raise NotImplementedError

    def should_update_records(self, record_identifiers: List[RecordIdentifier]) -> List[RecordIdentifier]:
        """
        Batch query database by computing all the keys and send them at once
        :param record_identifiers: all the record_identifiers that need to fetch from database
        :return:
            boolean mask of whether the record_identifier at that index require update
        """
        # initialize results with len(record_identifiers) and each value True indicating all entries needs update

        # build log for fast referecing. Mapping of record_key -> (index_in_record_identifiers)
        # query database for list of ids
        cursor = self.store.query(criteria={"record_key":
                                                {"$in": [r.record_key for r in record_identifiers]}},
                                  properties=["record_key", "state_hash", "last_updated"])

        not_exists = object()
        db_record_log = {doc["record_key"]: doc["state_hash"] for doc in cursor}
        to_update_list = [recordID.state_hash != db_record_log.get(recordID.record_key, not_exists) for recordID in
                          record_identifiers]
        return [recordID for recordID, to_update in zip(record_identifiers, to_update_list) if to_update]

    def assimilate(self, path: Path):
        """
        Main function that goes through each step and update the database
            - Step 1 Crawl through Path of the folder where data live to get RecordIdentifer Mapping
            - Step 2: For each RecordIdentifier from Step 1,  determine if it should be updated or not
            - Step 3: If needed, Process the Record (convert the Record into MongoDB data) (abstract function)
            - Step 4: Inject back the meta data
            - Step 5: Inject into the data base
        :param path: path in which files are read
        :param debug: if true, print hint information for program status
        :return:
            None
        """
        record_identifiers: List[RecordIdentifier] = self.read(path=path)  # step 1

        for rid in record_identifiers:
            self.logger.debug(msg="Discovered rid = {}".format(rid.record_key))

        records_to_update = self.should_update_records(record_identifiers)  # step 2

        if len(records_to_update) == 0:
            self.logger.debug(msg="No records need to be updated")
        else:
            for rid in records_to_update:
                self.logger.debug(msg="Need to update rid = {}".format(rid.record_key))

        batched_data = [{**self.compute_data(recordID=record_identifier), **record_identifier.dict()}
                        for record_identifier in records_to_update]  # Step 3 prepare record for update

        if len(batched_data) > 0:
            self.store.update(batched_data)  # step 5

        for d in batched_data:
            self.logger.debug(msg="Updated rid = {}".format(d.get("record_key")))

    def get_items(self) -> Iterable:
        record_identifiers: List[RecordIdentifier] = self.read(path=self.path)
        # So should we do database query natively in this method?
        records_to_update = self.should_update_records(record_identifiers)
        return records_to_update

    def update_targets(self, items: List):
        self.logger.info("Starting update in {} Builder".format(self.__class__.__name__))

        batched_data = [{**self.compute_data(recordID=record_identifier), **record_identifier.dict()}
                        for record_identifier in items]
        if len(batched_data) > 0:
            self.logger.info("Updating {} items".format(len(batched_data)))
            self.store.update(batched_data)
        else:
            self.logger.info("There are no items to update")

    def process_item(self, item: Any) -> Any:
        """
        move list comprehension in update_targets here

        :param item:
        :return:
        """
        pass


