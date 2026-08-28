"""Main application initialization and lifespan management for Object Detection API."""

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.routes import router, init_detector
from app.config import API_TITLE, API_DESCRIPTION, API_VERSION


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model detector at startup; clean up on shutdown."""
    print("Starting Object Detection API ...")
    try:
        # Initialize detector logic
        init_detector()
        print("Initialization completed successfully.")
    except Exception as exc:
        print(f"FATAL ERROR: Failed to initialize application: {exc}")
        raise
    yield
    print("Stopping application...")


# ── App Instance ─────────────────────────────────────────────────────
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan,
)

# ── Router inclusion ─────────────────────────────────────────────────
app.include_router(router)
