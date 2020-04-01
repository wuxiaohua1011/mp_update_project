from pydantic import BaseModel, Field
from pathlib import PosixPath, Path
from datetime import datetime
from typing import Dict, List
from monty.json import MSONable
from _hashlib import HASH as Hash
import hashlib
from abc import abstractmethod


class Document(BaseModel):
    path: PosixPath = Field(..., title="Path of this file")
    name: str = Field(..., title="File name")
    is_folder: bool = False


class RecordIdentifier(BaseModel):
    """
    The meta data for a record
    """
    last_updated: datetime = Field(..., title="The time in which this record is last updated")
    documents: List[Document] = Field(..., title="List of documents this RecordIdentifier indicate")
    record_key: str = Field(...,
                            title="Hash that uniquely define this record, can be inferred from each document inside")
    state_hash: str = Field(..., title="Hash of the state of the documents in this Record")


class Drone(MSONable):
    """
    An abstract drone that handles operations with database
    User have to implement all abstract methods to specify the data that they want to use to interact with this class


    - Step 1(readRecord):
        - Crawl through Path of the folder where data live
            - it will return Record of  (Already in method 2)
                (citations-1.bibtex, text-1.txt)
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

    def organizeDocuments(self, documents) -> Dict[str, List[Document]]:
        """
        a dictionary that maps RecordIdentifierKey -> [File Paths]
            ex:
            1 -> [citations-1.bibtex(Represented in Document), text-1.txt(Represented in Document)]
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

    def computeStateHash(self, doc: Document, digest=hashlib.md5()) -> Hash:
        """
        TODO: Ask Shyam whether I should move it to child classes
        Given a document, return the hash of the document
        :param doc: the document to hash
        :param digest: Hash instance that outer class used, if not provided, initiate a new one
        :return:
            Hash object that represent the Hash of this file
        """
        digest.update(doc.name.encode())
        with open(doc.path.as_posix(), 'rb') as file:
            buf = file.read()
            digest.update(buf)
        return digest

    def computeStateHashes(self, doc_list: List[Document]) -> str:
        """
        Given a list of documents, contain their hashes
        :param doc_list: list of documents
        :return:
            hash of the list of documents passed in
        """
        digest = hashlib.md5()
        for doc in doc_list:
            digest = self.computeStateHash(doc, digest)
        return str(digest.hexdigest())

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
                                            record_key=record_key,
                                            state_hash=self.computeStateHashes(doc_list))

        return recordIdentifier

    def read(self, path: Path) -> List[RecordIdentifier]:
        """
        Given a folder path to a data folder, read all the files, and return a dictionary
        that maps each RecordKey -> [File Paths]

        ** Note: require user to implement the function computeRecordIdentifierKey

        :param path: Path object that indicate a path to a data folder
        :return:

        """
        documents = self.generateDocuments(folder_path=path)
        log = self.organizeDocuments(documents=documents)
        record_identifiers = [self.computeRecordIdentifier(record_key, doc_list)
                              for record_key, doc_list in log.items()]
        return record_identifiers

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
        record_in_data_base = self.store.query_one(criteria={self.record_key: record_identifier.record_key})
        if record_in_data_base is None:
            return True
        record_in_data_base = RecordIdentifier.parse_obj(record_in_data_base)
        if record_in_data_base.state_hash != record_identifier.state_hash:
            return True
        else:
            return False

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
                    "citation": citations-1.bibtex ,
                    "text": text-1.txt
                }

        """
        raise NotImplementedError

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
        batched_data = []
        record_identifiers = self.read(path=path)  # step 1
        for record_identifier in record_identifiers:  # step 2
            if self.shouldUpdateRecord(record_identifier=record_identifier):  # step 2
                data = self.computeData(recordID=record_identifier)  # step 3
                data.update(record_identifier.dict())  # step 4
                batched_data.append(data)
            else:
                if debug:
                    print("No need to update Record with ID {}".format(record_identifier.record_key))

        if len(batched_data) > 0:
            if debug:
                for b in batched_data:
                    print("Updating Record With ID {}".format(b[self.record_key]))
            self.store.update(batched_data)  # step 5
