from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="scaffold-api", version="0.1.0")


class HealthResponse(BaseModel):
    status: str
    version: str


@app.get("/health")
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version="0.1.0")
