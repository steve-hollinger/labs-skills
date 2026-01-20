"""API for health check exercise."""

import os
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"service": "api", "status": "running"}
