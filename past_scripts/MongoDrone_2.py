from hashlib import md5
from os import listdir
from os.path import isfile, join
from pathlib import Path
from typing import List, Dict, Union

from maggma.stores import MongoStore  # type: ignore
from pydantic import BaseModel, Field

from past_scripts.drone_2 import Drone


class Document(BaseModel):
    """
    Representation of a document and its md5sum
    """
    fpath: str = Field(..., title="File Path")
    md5sum: str = Field(..., title="md5sum of the file")

class RecordIdentfier(BaseModel):
    date: Field()
    fname: Field()
    state_hash: Field()
    documents: Dict[str, str] = Field(..., title="Dictionary of fpath to md5sum in this record")
    # (md5sum of the file names)
    # (md5sum of the md5sum of the files)

# class Record(BaseModel):
#     """
#
#     Representation of list of related documents
#     """
#     identifier: str = Field(..., title="ID of the record")
#     documents: Dict[str, Document] = Field(..., title="Dictionary of fpath to Documents in this record")


class MongoDrone(Drone):
    def __init__(self, store: MongoStore):
        super().__init__(store)

    def computeRecordIdentifier(self, document: BaseModel) -> str:
        document = Document.parse_obj(document)
        fname = Path(document.fpath).name
        prefix, postfix = fname.split(sep="-", maxsplit=1)
        ID, ftype = postfix.split(sep=".", maxsplit=1)
        return ID

    def buildRecords(self, documents: Union[List[BaseModel], Path], debug=False):
        if isinstance(documents, Path):
            documents = self.readFiles(documents)
        for document in documents:
            document = Document.parse_obj(document)
            record_identifier = self.computeRecordIdentifier(document=document)
            record: Record = self.store.query_one(criteria={"identifier": record_identifier})
            if record is None:
                if debug:
                    print("Have not seen record {}".format(record))
                self.insertNewRecord(Record(identifier=record_identifier,
                                            documents={document.fpath: document}),
                                     debug=debug)
            else:
                record = Record.parse_obj(record)
                if debug:
                    print("Have seen record {}".format(record))
                self.update(document, record, debug=debug)
            if debug:
                print()

    def readFiles(self, folder_path: Path, debug=False) -> List:
        files_paths = [folder_path / f for f in listdir(folder_path.as_posix()) if
                       isfile(join(folder_path.as_posix(), f))]
        docs = [self.createDoc(file_path=f) for f in files_paths]
        if debug:
            print("read_files Debug: ")
            for d in docs:
                print("     -->{}".format(d))
            print()
        return docs

    def update(self, doc: BaseModel, record: BaseModel, debug=False):
        doc = Document.parse_obj(doc)
        record = Record.parse_obj(record)
        if doc.fpath in record.documents.keys():
            if record.documents[doc.fpath].md5sum != doc.md5sum:
                if debug:
                    print(" --> <{}> has changed".format(doc))
                record.documents[doc.fpath] = doc
                self.store.update(record.dict())
                print("Single Record Updated")
            else:
                if debug:
                    print(" --> <{}> has not changed".format(doc))
        else:
            if debug:
                print(" --> <{}> is not in record yet".format(doc))
            record.documents[doc.fpath] = doc
            self.store.update(record.dict())

    def createDoc(self, file_path: Path) -> Document:
        """
        Creates Document from a single file
        :param file_path:
        :return:
        """
        with open(file_path.as_posix(), 'rb') as file:
            s = file.read()
        md5sum = md5(s).hexdigest()
        d = Document(fpath=file_path.as_posix(), md5sum=md5sum)
        return d

    def insertNewRecord(self, record: Record, debug=False):
        if debug:
            print(" --> Inserting New Record {}".format(record))
        self.store.update(record.dict())


if __name__ == "__main__":
    store = MongoStore(database="drone_test", collection_name="drone_test", key="identifier")
    store.connect()

    mongo_drone = MongoDrone(store=store)

    mongo_drone.buildRecords(Path.cwd() / "data" / "example1", debug=False)
