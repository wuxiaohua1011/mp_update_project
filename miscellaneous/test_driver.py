import uvicorn
from fastapi import FastAPI, Header, HTTPException
from materialsProject2.routers.example_material import example_material

app = FastAPI()
app.include_router(
    example_material.router,
    prefix="/materials",
    tags=["materials"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
