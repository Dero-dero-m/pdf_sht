from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import get_settings


class HealthResponse(BaseModel):
    status: str
    version: str


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="scaffold-api", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse(status="ok", version="0.1.0")

    return app


app = create_app()
