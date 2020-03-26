from monty.json import MSONable  # type: ignore
from maggma.core import Store  # type: ignore
from pydantic import BaseModel, Field
from typing import List, Dict, Union
from pathlib import Path


class Drone(MSONable):
    """
    Abstract class that support
    1. store Records
    2. detect if any Record changed
        - If it did change, update that individual Record

    Note: a concrete drone must support these functionalities:
    1. the specific store that is used
    2.
    """

    def __init__(self,
                 store: Store,
                 ):
        self.store = store

    def computeRecordIdentifier(self, document: BaseModel) -> str:
        """
        Computes the record identifier(key) from document
        :param document:
        :return:

        """
        raise NotImplementedError

    def buildRecords(self, documents: Union[List[BaseModel], Path], debug=False):
        """
        Read files from folder_path
        :param documents: List of document/ file Path to read the documents from
        :param debug: if True, print what's read
        """
        raise NotImplementedError

    def read_files(self, folder_path: Path, debug=False) -> List:
        """
        Read files from folder_path and return a list of documents(which may be folders themselves)
        :param folder_path: desired path to read
        :param debug: if True, print what's read
        :return:
            list of docuemtns
        """
        raise NotImplementedError

    def update(self, doc: BaseModel, record: BaseModel, debug=False):
        """
        detect if any Record changed, if it did change, update that individual Record
        :return: True if one of the document is updated, false if none are updated
        """
        raise NotImplementedError



