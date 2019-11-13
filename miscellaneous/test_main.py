from fastapi import FastAPI, Query, Form
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None


@app.get("/")
async def root():
    return {"message": "Hello World"}


# @app.get("/items/{item_id}")
# async def read_item(item_id):
#     return {"item_id": item_id}

@app.post("/login/")
async def login(*, username: str = Form(...), password: str = Form(...)):
    return {"username": username}
