from fastapi import FastAPI

from api.v1.endpoints import analysis

app = FastAPI(title="Aegis AI")


@app.get("/")
def read_root():
    return {"message": "Aegis AI is online"}


app.include_router(
    analysis.router,
    prefix="/api/v1",
    tags=["Analysis"],
)
