"""
[DONE] 1.) Make a folder
[DONE] 2.) Add bibtex files - using bibtex to store information on papers
    - one citation
3.) Write a drone that does the following
    - identify all unique bibtex files to ingest [still need to do this]
    - converts the bibtex file into a document for MongoDB [Done]
    - adds metadata to be able to track file->document relationship [Partially, need to add more unique fields]
4.) Runner
    - Using a drone find all files to process
    - process those files -> in parallel according to input parameters [NOT QUITE SURE HOW TO DO PARALLEL IN PYTHON]
    - push the documents to a maggma store
Run the runner once
change a single file
Run the runner again - it should just update that one file into the Database
"""
from util03242020py import *


def record_current_state(store: MemoryStore, fname=Path("records.txt")):
    cursor = store.query(criteria={})
    fname = fname.as_posix()
    data = []
    if os.path.exists(fname):
        print("The file <{}> exist, removing it and creating an new one".format(fname))
        os.remove(fname)
    else:
        print("The file <{}> does not exist".format(fname))

    while True:
        try:
            item = next(cursor)
        except StopIteration:
            break
        doc = Document(**item)
        data.append(doc.dict())

    with open(fname, 'w+') as json_file:
        # convert from Python dict-like structure to JSON format
        jsoned_data = json.dumps(data, indent=True)
        json_file.write(jsoned_data)
    print("Record written successfully")


docs = get_list_of_files(folder_path=Path.cwd() / "data", debug=False)
store = populate_mongo_store(documents=docs)
record_current_state(store)

