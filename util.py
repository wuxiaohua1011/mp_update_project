from maggma.stores import MemoryStore
from pydantic import BaseModel, Field
from os import listdir
import os
from os.path import isfile, join
from pathlib import Path
import hashlib
from typing import List
import json


# document model: fpath -> md5sum
class Document(BaseModel):
    """
    mapping the file at fpath to its md5sum
    """
    fpath: str = Field(..., title="File Name")
    md5sum: str = Field(..., title="md5sum of the file")


def get_list_of_files(folder_path: Path, debug=False) -> List[Document]:
    """

    :param folder_path: folder path that want to list the files
    :param debug: print out files
    :return:
        return a list of Document objects for the folder path
    """
    files_paths = [folder_path / f for f in listdir(folder_path.as_posix()) if
                   isfile(join(folder_path.as_posix(), f)) and f != ".DS_Store"]
    result = []
    for f in files_paths:
        with open(f.as_posix(), 'rb') as file:
            s = file.read()
        md5sum = hashlib.md5(s).hexdigest()
        d = Document(fpath=f.as_posix(), md5sum=md5sum)
        result.append(d)
    if debug:
        print("Filepath -> md5sum")
        for document in result:
            print("     -> {} --> {}".format(document.fpath, document.md5sum))
        print()
    return result


def populate_mongo_store(documents: List[BaseModel], collection_name="docuemnts", key="fpath") -> MemoryStore:
    store = MemoryStore(collection_name=collection_name, key=key)
    store.connect()
    doc_dicts = [d.dict() for d in documents]
    store.update(doc_dicts)
    return store