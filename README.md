# Materials Project Backend Modularization Test

## A. Introduction & Purpose
Michael Wu's second apprenticeship at LBNL, supervised & Mentored by [Shyam Dwaraknath](https://www.linkedin.com/in/shyam-dwaraknath/)

Project's Goal is to explore how to make the Material Project's backend system to become more modular, ensuring that data transfer is more pipelined, and development of an individual component is standardized.

## B. Tools used
- [FastAPI](https://github.com/tiangolo/fastapi)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [Dash](https://plot.ly/dash/)

## C. Progress


### Dec 26, 2019
    1. have tags in cluster manager when initialize endpoint clusters
        - Done, tags = [] when not passed in
    2. look at bigger application in fastapi, see if there's any other optional params that we can incluce
    3. implement responses (cluster manager can override endpoints'), and application.py
    4. write documentation in Google Docstrings format
        - done, also found out about doc string from Swagger UI, might be useful?
        - https://fastapi.tiangolo.com/tutorial/path-operation-configuration/#description-from-docstring
    5. push everything to refactor branch of maggma
        - Done, but task 2 and 3 will be synced manually a little later

### Dec 10, 2019
Commit:
1. distint added in the root(endpoint_cluster.py)

2. query on formula added on materials_endpoint
3. more test written for formula

Problems:
1. cannot test for root endpoint stuff, see the commented out section in maggma/tests/test_endpoint_cluster.py
2. currently creating a seperate endpoint is still pretty complicated, need to fiture out a systematic way
3. need to write more documentation for the code

### Dec 6, 2019
1. create a pull request for `maggma refactor`
    - make the `endpointcluster.py` in the main maggma folder(where builders.py is)
    - Done, but need to ask Shyam how to organize these files, and also where exactly does the dependency comes in
2. pagination -- dependency
    - fastapgit i -> dependency   
    - HATEOS
    - Pagination Dependency added
        - put the dependency class in `example_models.py` because all endpoints should be using common pagination
3. Try play with GraphQL-pydantic --query parsing language

### Dec 5, 2019
1. updating maggma branch.
    - encountered problem with writing unnittest -- it does not recognize root endpoint for some reason but does recognize materials endpoint
    - understood and implemneted a dummy pydantic graphql, trying to think about how to plug it in for our project
    

### Nov 11, 2019
1. Skip and limit in constructor and apply them throughout different functions that requires it
    - Done
2. Endpoint.run() to simplify running
    - Done
3. Rename the class name to something else, read up on REST framework to see what's the technical name
    - EndpointCluster/Endpoints
        - https://docs.couchbase.com/server/current/rest-api/rest-endpoints-all.html
    - REST API design tips -- https://github.com/ptboyer/restful-api-design-tips
4. move to Maggma, below are the attributes that all abstract classes should already implement
    - Task_id
    - last_updated
    - errors
    - warnings
    - boolean to enable/disable search on warnings
    1. in main.py, i think we are already using maggma.JSONSTORE as our database connection, so I think we are good?
5. implement test using FastAPI testing framework
    - welp, how do i compare json??
    - use `pytest --disable-pytest-warnings` to suppress warnings
    - ask shyam for a more formal way of doing pytest, having a picked database or something?
6. research and design how to develop a wrapping class for each "endpoint" such that we can ex:query different databases
7. build a simple form (POST) operation
    - I think this is the right thing but im not sure how to correctly test it to make sure it is working
        -         # https://www.errietta.me/blog/python-fastapi-intro/
        -         # https://fastapi.tiangolo.com/tutorial/request-forms/

### Oct, 25, 2019 
- pass in data_type(ex Material) into the Endpoint __init__
    - make sure all of the get methods follow the data_type
    - implement dynamic dispatch --> if the data attribute is in the data_type, then create the route
- How to add pagination into the queries that needs it (Make sure all routes needs it)
- How activate a 404 response on task_id
- Add a few more routes
    - Searching by "errors" field
    - searching by "warnings" field
    - create a route that can give me all distinct choices
        - hint: pymongo has a function to do it, its in maggma
        - if i want to search it, how do i know what different options do i have?
        - design it such that its not 1000000 different routes
       

### Oct 18, 2019
- Deploy app using APIRouter
    - Have to invoke app at the lbnl directory using `uvicorn materialsProject2.main:app --reload`
    - this issue has something to do with relative import path in the `materialsProject2/main.py` file, line 2
- Understand Uvicorn load structure to write a script that can programmatically start server
    - https://www.uvicorn.org/
    - okay, got it, super simple. see test_driver.py
- Need help with python file structure.... idk how to resolve this issue....
    - nvm, got it

    

### Sep 27, 2019
- Use choices for crystal system
    - Done

- Switch to using Memory store to hold your documents and for all your searches
    - Used JSONStore, which inherits MemoryStore
- Try JSONStore as well
    - JSONStore turns out to be really easy to use. 
    - install the [maggma](https://github.com/materialsproject/maggma/blob/master/maggma/) repository by source
    - see main.py for usage example, specifically the `get_on_task_id` function
    - other function has not been modified yet, need to review if PyMongo already have some similar functions so that I am not re-inventing the wheel
- How to see model definition in swagger
    - Done
    - It doesn't seem like GET would return any schema, but PUT does. 
    - To see the result, please do
        - `uvicorn main:app --reload`
        - go to `http://127.0.0.1:8000/docs`
        - OR `http://127.0.0.1:8000/redoc`
5. Wildcards in chemsys and formula: Ba*O3 
    - should match BaTiO3, BaEuO3, but not BaTi2O3, Ba-*-O should match Ba-Ti-O, Ba-Eu-O, etc. 
    - Have not gotten to this part yet


### Sep 19, 2019
- For the model's symmetry --> crystal_system --> make an enumeration since there's only these choices
    - `["tetragonal","triclinic","orthorhombic","monoclinic","hexagonal","cubic","trigonal"]`
    - Unable to achieve this task this week because after some research, it seems like adding additional checking into Pydantic models requires a lot of work
        -  like i need to enforce this before it is being passed into the model, which complicates the matter, going to ask Shyam if he has any experience on this before i start
- Find based on formula:
    - `BiTiO3, BiO3Ti, TiBiO3` are equivalent
    - done through using Pymatgen's `pymatgen.core.composition` class
- put everything under common endpoint
    - Done
- Make a universial search at the root endpoint
    - Done, it will redirect to its respective common endpoint, currently really naive logic, but it works
    - ask Shyam if there's any edge cases that I am not considering



#### Sep 13, 2019
- Built a simple and rudimentary model based on the data Shyam provided. 
    - The Materials model is located at models.py, using Pydantic
- Built a simple example of "search on chemsys", file located at `miscellaneous/chemsys_search.py`
    - To test:
        1. `pytest chemsys_search.py`
- Built a simple endpoint to serve materials docs based on task_id and to search based on chemsys
    - To run: 
        1. `uvicorn main:app --reload`
        2. For serve based on task_id, go to your favorite browser, and type `http://127.0.0.1:8000/task_id/mp-1008501`
        3. For search based on chemsys, go to your favorite browser, and type `http://127.0.0.1:8000/materials/?chemsys=Be`


- Initialized this Github Repository and added some gitignores
#### Sep 4, 2019
- Looked through and did some of the tutorials for 
    - [FastAPI](https://github.com/tiangolo/fastapi)
    - [Pydantic](https://pydantic-docs.helpmanual.io/)
    - [Dash](https://plot.ly/dash/)
- Set up a temporary meeting time with Shyam due to class scheduling is still in progress

