"""Main application initialization and lifespan management for Object Detection API."""

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.routes import router, init_detector
from app.config import (
    ALLOWED_ORIGINS,
    API_DESCRIPTION,
    API_TITLE,
    API_VERSION,
    RATE_LIMIT_PER_MINUTE,
)
from app.security import (
    RateLimiterMiddleware,
    SafeExceptionMiddleware,
    SecurityHeadersMiddleware,
)
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model detector at startup; clean up on shutdown."""
    print("Starting Object Detection API with Enhanced Security Layers ...")
    try:
        # Initialize detector logic
        init_detector()
        print("Initialization completed successfully. Security layers active.")
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

# ── Security Middlewares (Order of execution: innermost to outermost) ─
# 1. Catch unhandled errors and prevent internal trace leaks
app.add_middleware(SafeExceptionMiddleware)

# 2. Sliding window rate limiting to block DoS and flooding
app.add_middleware(RateLimiterMiddleware, requests_per_minute=RATE_LIMIT_PER_MINUTE)

# 3. HTTP Security Headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options)
app.add_middleware(SecurityHeadersMiddleware)

# 4. Cross-Origin Resource Sharing (CORS) protection
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if "*" not in ALLOWED_ORIGINS else ["*"],
    allow_credentials=True if "*" not in ALLOWED_ORIGINS else False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ── Router inclusion ─────────────────────────────────────────────────
app.include_router(router)

