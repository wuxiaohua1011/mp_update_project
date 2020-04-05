from pydantic import BaseModel, Field
from pathlib import PosixPath, Path
from datetime import datetime
from typing import Dict, List, Optional
from monty.json import MSONable
from _hashlib import HASH as Hash
import hashlib
from abc import abstractmethod
import os.path

class Document(BaseModel):
    path: PosixPath = Field(..., title="Path of this file")
    name: str = Field(..., title="File name")
    is_folder: bool = False


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
        Given a list of documents, contain their hashes
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


class Drone(MSONable):
    """
    An abstract drone that handles operations with database
    User have to implement all abstract methods to specify the data that they want to use to interact with this class


    - Step 1(readRecord):
        - Crawl through Path of the folder where data live
            - it will return Record of  (Already in method 2)
                (cite.bibtex, data.txt)
                (citations-2.bibtex, text-2.txt)
                (citations-3.bibtex, ) ...
     - Step 2: Takes a list of Record (from the result above), and say if it should be updated or not
        - If you've seen it before and the raw data has changed --> return True
        - If you never seen it before --> return True
        - Otherwise --> return False
     - Step 3: Process the Record (convert the Record into MongoDB data) (abstract function)
     - Step 4: Inject back the meta data to see if the Record if needed to be updated
     - Step 5: Inject into the data base
    """

    def __init__(self,
                 store,
                 record_key):
        self.store = store
        self.record_key = record_key

    @abstractmethod
    def computeRecordIdentifierKey(self, doc: Document) -> str:
        """
        Compute the RecordIdentifier key that this document correspond to
        :param doc: document which the record identifier key will be inferred from
        :return:
            RecordIdentifiierKey
        """
        raise NotImplementedError

    @abstractmethod
    def generateDocuments(self, folder_path: Path) -> List[Document]:
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
    def computeData(self, recordID: RecordIdentifier) -> Dict:
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

    def shouldUpdateRecords(self, record_identifiers: List[RecordIdentifier]) -> List[bool]:
        # initialize results with len(record_identifiers) and each value True indicating all entries needs update
        result = [True] * len(record_identifiers)

        # build log for fast referecing. Mapping of record_key -> (index_in_record_identifiers)
        memory_record_identifiers_log = {record_identifiers[i].record_key: i for i in range(len(record_identifiers))}
        keys = [r.record_key for r in record_identifiers]
        print("DEBUG: All Keys to Check {}".format(keys))
        # query database for list of ids
        cursor = self.store.query(criteria={self.record_key:
                                                {"$in": [r.record_key for r in record_identifiers]}},
                                  properties=["record_key", "state_hash", "last_updated"]) # TODO check with Shyam here

        while True:
            try:
                database_record_id: RecordIdentifier = RecordIdentifier.parse_obj(next(cursor))
                # find the corresponding index in record_identifiers list and compare their state hash
                index = memory_record_identifiers_log.get(database_record_id.record_key, -1)
                assert index != -1, "ERROR: Something went wrong, record in database queried not found in memory"
                memory_record_id = record_identifiers[index]
                if memory_record_id.state_hash == database_record_id.state_hash:
                    result[index] = False
            except StopIteration:
                break
        print()
        return result

    def shouldUpdateRecord(self, record_identifier: RecordIdentifier) -> bool:
        """
        - If you never seen it before --> return True
        - If you've seen it before and the raw data has changed --> return True
        - Otherwise --> return False

        :param record_identifier: The Record to query if the database has it or not, or if its state has changed
        :return:
            True if you've seen the record before and the raw data has changed or you never seen the record before
            False otherwise
        """
        record_in_data_base = self.store.query_one(criteria={self.record_key: record_identifier.record_key},
                                                   properties=["record_key", "state_hash", "last_updated"])
        if record_in_data_base is None:
            return True
        record_in_data_base = RecordIdentifier.parse_obj(record_in_data_base)
        if record_in_data_base.state_hash != record_identifier.state_hash:
            return True
        else:
            return False

    def assimilate(self, path: Path, debug=False):
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
            print(rid.state_hash)

        update_mask: List[bool] = self.shouldUpdateRecords(record_identifiers)  # step 2

        records_to_update = [recordID for recordID, update in zip(record_identifiers, update_mask) if update]

        batched_data = [{**self.computeData(recordID=record_identifier), **record_identifier.dict()}
                        for record_identifier in records_to_update]  # Step 3 prepare record for update

        if len(batched_data) > 0:
            if debug:
                for b in batched_data:
                    print("Updating Record With ID {}".format(b[self.record_key]))
            self.store.update(batched_data)  # step 5
