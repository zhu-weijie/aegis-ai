from fastapi import FastAPI

from api.v1.endpoints import analysis, threat_intel

app = FastAPI(title="Aegis AI")


@app.get("/")
def read_root():
    return {"message": "Aegis AI is online"}


app.include_router(
    analysis.router,
    prefix="/api/v1",
    tags=["Phishing Analysis"],
)
app.include_router(
    threat_intel.router,
    prefix="/api/v1",
    tags=["Threat Intelligence"],
)
