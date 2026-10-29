from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import compatibility, parts, search, vehicles
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Compatibilidad de autopartes con vehículos (marca, modelo, año, motor).",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (vehicles.router, parts.router, compatibility.router, search.router):
    app.include_router(router, prefix="/api")


@app.get("/api/health", tags=["Sistema"])
def health():
    return {"status": "ok"}
