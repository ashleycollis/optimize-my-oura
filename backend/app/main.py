from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .routes import router as api_router
from .db import engine
from .models import Base

settings = get_settings()
app = FastAPI(title=settings.app_name)

# CORS will be finalized once env is wired; allow localhost during dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(api_router)


@app.on_event("startup")
def on_startup() -> None:
    # Create tables if they don't exist yet (dev convenience; replace with Alembic later)
    Base.metadata.create_all(bind=engine)


