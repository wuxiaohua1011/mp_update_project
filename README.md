# Materials Project Backend Modularization Test

## A. Introduction & Purpose
Michael Wu's second apprenticeship at LBNL, supervised & Mentored by [Shyam Dwaraknath](https://www.linkedin.com/in/shyam-dwaraknath/)

Project's Goal is to explore how to make the Material Project's backend system to become more modular, ensuring that data transfer is more pipelined, and development of an individual component is standardized.

## B. Tools used
- [FastAPI](https://github.com/tiangolo/fastapi)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [Dash](https://plot.ly/dash/)

## C. Progress
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

