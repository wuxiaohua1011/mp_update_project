# Materials Project Backend Modularization Test

## A. Introduction & Purpose
Michael Wu's second apprenticeship at LBNL, supervised & Mentored by [Shyam Dwaraknath](https://www.linkedin.com/in/shyam-dwaraknath/)

Project's Goal is to explore how to make the Material Project's backend system to become more modular, ensuring that data transfer is more pipelined, and development of an individual component is standardized.

## B. Tools used
- [FastAPI](https://github.com/tiangolo/fastapi)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [Dash](https://plot.ly/dash/)

## C. Progress

### Oct 18, 2019
- Deploy app using APIRouter
    - Have to invoke app at the lbnl directory using `uvicorn materialsProject2.main:app --reload`
    - this issue has something to do with relative import path in the `materialsProject2/main.py` file, line 2
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

