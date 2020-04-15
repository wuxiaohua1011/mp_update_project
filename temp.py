

"""
https://github.com/hackingmaterials/atomate/blob/master/atomate/vasp/drones.py
Drone
    - A list of files that have patterns in names
        - whatever in the bibtex is the data, whatever in the txt is the meta data
    - Step 1:
        - Crawl through Path of the folder where data live
            - it will return Record of  (Already in method 2)
                (cite.bibtex, data.txt)
                (cite2.bibtex, text-2.txt)
                (citations-3.bibtex, ) ...
     - Step 2: Takes a list of Record (from the result above), and say if it should be updated or not
        - If you've seen it before and the raw data has changed --> return True
        - If you never seen it before --> return True
        - Otherwise --> return False
     - Step 3: Process the Record (convert the Record into MongoDB data) (abstract function)
     - Step 4: Inject back the meta data to see if the Record if needed to be updated
     - Step 5: Inject into the data base
"""


# database IO is always expensive

"""
Optimization
assimilate
    - 


"""

# for record_identifier in records_to_update:  # step 2
#     # if self.shouldUpdateRecord(record_identifier=record_identifier):  # step 2 <- build a function that given a list of RecordID, give back a list indicating which recordID should be upadated
#     data = self.computeData(recordID=record_identifier)  # step 3
#     data.update(record_identifier.dict())  # step 4
#     batched_data.append(data)

"""
New things:
- make example1 and exmaple2 work in BibTexDrone

- profiling to see which part is slow
    -  https://docs.python.org/3/library/profile.html
- implement a custom RecordIdentifier class that have custom hash, etc
- a read function that returns the shape of the system file structure it sees. 
- 



"""





"""
in the future, use python's logging function for debug printing


Drone.py inherit from MSONABLE, nand ABC Meta

Switch docstring to Arguments:
Return 
    should UpdateRecord should return a list of recordIdentifer being updated

    Two types of RecordIdentifier
        I care about


    move computeRecord key into the recordIdentifier
        - default key name is going to be hash of all the document

    document should be not be a directory, document should always be a file

    for loop on cursor in shouldUpdateRecords(see slack)


    remove printTree function


BibTexDrone


source=[]


Builder
    keep read and computeData
    any database related function can only happen in getUpdate and get_items
    anything that can be paralleled, should be in process
"""


"""
Drone(Builder)

Inherit from Builder

Builder.run()

put things that can be put into process_item

mrun, run builder in parallel

"""