

"""
https://github.com/hackingmaterials/atomate/blob/master/atomate/vasp/drones.py
Drone
    - A list of files that have patterns in names
        - whatever in the bibtex is the data, whatever in the txt is the meta data
    - Step 1:
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


from pydantic import BaseModel, Field
test_data = {"f1": "st1",
             "f2": "st2",
             "f3": "st3"}


class TestModel(BaseModel):
    f1: str = Field(...)
    f2: str = Field(...)

t = TestModel.parse_obj(test_data)
# t = TestModel(**test_data)
print(t)