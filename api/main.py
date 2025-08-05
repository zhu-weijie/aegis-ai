from fastapi import FastAPI

app = FastAPI(title="Aegis AI")


@app.get("/")
def read_root():
    return {"message": "Aegis AI is online"}
