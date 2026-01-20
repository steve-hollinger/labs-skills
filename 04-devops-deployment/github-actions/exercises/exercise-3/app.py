"""Sample application for deployment exercise."""

import os
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello from the deployed app!"}


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
    }
