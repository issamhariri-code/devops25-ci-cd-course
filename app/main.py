from fastapi import FastAPI, HTTPException
from app.service import add, divide

app = FastAPI(title="DEVOPS25 CI/CD Demo")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/add")
def api_add(a: int, b: int):
    return {"result": add(a, b)}


@app.get("/api/divide")
def api_divide(a: float, b: float):
    try:
        return {"result": divide(a, b)}
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

@app.get("/version")
def api_version():
    return {"version": "1.0.1"}
