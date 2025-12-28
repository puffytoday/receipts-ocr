from typing import Dict
from fastapi import FastAPI

app = FastAPI(title="Expense Tracker API")


@app.get("/")
def get_root() -> Dict[str, str]:
    return {"message": "Expense tracker API is running"}


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}
