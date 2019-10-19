from fastapi import FastAPI, Header, HTTPException
from .routers.example_material import example_material

app = FastAPI()


async def get_token_header(x_token: str = Header(...)):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


app.include_router(
    example_material.router,
    prefix="/materials",
    tags=["materials"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

