from util import *


# docs = get_list_of_files(folder_path=Path.cwd() / "data", debug=False)
# store = populate_mongo_store(documents=docs)


def read_records(fname: Path = Path("records.txt")) -> List[BaseModel]:
    fname = fname.as_posix()
    documents = []
    with open(fname, 'r') as json_file:
        json_data = json.load(json_file)
    for j in json_data:
        doc = Document(**j)
        documents.append(doc)
    return documents


documents = read_records()
store = populate_mongo_store(documents)

current_docs: List[Document] = get_list_of_files(folder_path=Path.cwd() / "data", debug=False)
for curr_doc in current_docs:
    old_doc = Document(**store.query_one(criteria={"fpath": curr_doc.fpath}))
    if old_doc.md5sum != curr_doc.md5sum:
        print("CAUGHT YOU! YOU MODIFIED <{}>".format(curr_doc.fpath))
