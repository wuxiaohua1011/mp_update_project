from util import *


# docs = get_list_of_files(folder_path=Path.cwd() / "data", debug=False)
# store = populate_mongo_store(documents=docs)

def printGenerator(generator):
    while True:
        try:
            item = next(generator)
            print("     --> {}".format(item))
        except StopIteration:
            break


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

changed_docs = []
current_docs: List[Document] = get_list_of_files(folder_path=Path.cwd() / "data", debug=False)

for curr_doc in current_docs:
    old_doc = Document(**store.query_one(criteria={"fpath": curr_doc.fpath}))
    if old_doc.md5sum != curr_doc.md5sum:
        print("CAUGHT YOU! YOU MODIFIED <{}>".format(curr_doc.fpath))
        changed_docs.append(curr_doc.dict())

if len(changed_docs) > 0:
    print("BEFORE: ")
    printGenerator(store.query(criteria={"fpath": {"$in": [doc.get("fpath") for doc in changed_docs]}}))

    store.update(changed_docs, key="fpath")  # this line does the update

    print("AFTER: ")
    printGenerator(store.query(criteria={"fpath": {"$in": [doc.get("fpath") for doc in changed_docs]}}))
else:
    print("Nothing was changed")


