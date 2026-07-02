from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api import devices, events, health, internal, locks, predictions
from backend.app.core.config import get_settings
from backend.app.db.session import Base, SessionLocal, engine
from backend.app.models import domain  # noqa: F401
from backend.app.services.seed import seed_demo_data


def create_app() -> FastAPI:
    settings = get_settings()
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_demo_data(db)

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Edge AI smart doorbell backend with ML and agentic scaffolding.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(devices.router)
    app.include_router(events.router)
    app.include_router(predictions.router)
    app.include_router(locks.router)
    app.include_router(internal.router)
    return app


app = create_app()
