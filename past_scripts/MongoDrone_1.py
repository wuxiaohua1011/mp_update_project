from os import listdir

from past_scripts.drone_2 import Document, Record, Drone
from maggma.stores import MongoStore
from typing import List, Dict
from pathlib import Path
from os.path import isfile, join
from hashlib import md5


class MongoDrone(Drone):
    """
    Concrete example of a drone using MemoryStore
    """

    def __init__(self,
                 store: MongoStore):
        super().__init__(store=store)

    def init_build_records(self, folder_path: Path, debug=False):
        """
        very costly operation
        :param folder_path:
        :param debug:
        :return:
        """
        files_paths = [folder_path / f for f in listdir(folder_path.as_posix()) if
                       isfile(join(folder_path.as_posix(), f))]
        records: Dict[str, Record] = dict()
        for f in files_paths:
            document = self.createDoc(f)
            key = self.computeRecordKey(document)
            if records.get(key, None) is not None:
                records[key].documents.append(document)
            else:
                r = Record(key=key, documents=[document])
                records[key] = r
        self.store.update(docs=[r.dict() for r in records.values()])
        print("Build finished")

    def read_files(self, folder_path: Path, debug=False) -> List[Document]:
        files_paths = [folder_path / f for f in listdir(folder_path.as_posix()) if
                       isfile(join(folder_path.as_posix(), f))]
        return [self.createDoc(file_path=f) for f in files_paths]

    def update(self, folder_path: Path):
        docs = self.read_files(folder_path)

    def createDoc(self, file_path: Path) -> Document:
        with open(file_path.as_posix(), 'rb') as file:
            s = file.read()
        md5sum = md5(s).hexdigest()
        d = Document(fpath=file_path.as_posix(), md5sum=md5sum)
        return d

    def computeRecordKey(self, document: Document) -> str:
        fname = Path(document.fpath).name
        prefix, postfix = fname.split(sep="-", maxsplit=1)
        ID, ftype = postfix.split(sep=".", maxsplit=1)
        return ID

    def isInstore(self, ID):
        return True if self.store.query_one(criteria={"key": ID}) is not None else False


if __name__ == "__main__":
    kwargs = {
        "database": "drone_test"
    }
    store = MongoStore(database="drone_test", collection_name="drone_test", key="key")
    store.connect()
    memory_drone = MongoDrone(store=store)

    memory_drone.init_build_records(Path.cwd() / "data" / "folder1")

    store.close()
