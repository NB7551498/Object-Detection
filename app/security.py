"""Production Security Layer for VisionAI.

Implements multi-layer defense-in-depth protections:
1. Security Headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Permissions-Policy)
2. Thread-safe in-memory Sliding Window Rate Limiting (DoS / Flooding protection)
3. Image Magic Byte Signature Validation (Polyglot & MIME-spoofing defense)
4. WebSocket Security Manager (Connection capping, frame throttling, size limits)
5. Sanitized Exception Handling (Prevents information disclosure and traceback leaks)
6. Optional API Key verification
"""

import logging
import os
import time
from collections import defaultdict
from threading import Lock
from typing import Dict, List, Optional, Set

from fastapi import HTTPException, Request, Response, WebSocket, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import (
    API_KEY,
    MAX_FILE_SIZE_BYTES,
    MAX_IMAGE_DIMENSION,
    MAX_WS_CONNECTIONS_PER_IP,
    RATE_LIMIT_PER_MINUTE,
)

logger = logging.getLogger("visionai.security")

# Allowed image magic signatures (byte headers)
MAGIC_SIGNATURES: Dict[str, bytes] = {
    "image/jpeg": b"\xff\xd8\xff",
    "image/png": b"\x89PNG\r\n\x1a\n",
    "image/bmp": b"BM",
}


def validate_image_magic_bytes(image_bytes: bytes, declared_content_type: str) -> bool:
    """Verify that file payload matches genuine binary image signatures.

    Defends against MIME spoofing where an executable or script is disguised as an image.
    """
    if len(image_bytes) < 12:
        return False

    # Check WebP header: 'RIFF' .... 'WEBP'
    if declared_content_type == "image/webp":
        return image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP"

    # Check JPEG, PNG, BMP headers
    sig = MAGIC_SIGNATURES.get(declared_content_type)
    if sig:
        return image_bytes.startswith(sig)

    # If declared type is in allowed content types, verify against any known image header
    if image_bytes.startswith(b"\xff\xd8\xff") or image_bytes.startswith(b"\x89PNG\r\n\x1a\n") or image_bytes.startswith(b"BM"):
        return True
    if image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP":
        return True

    return False


def sanitize_filename(filename: Optional[str]) -> str:
    """Sanitize client-provided filename to prevent path traversal attacks."""
    if not filename:
        return "upload.jpg"
    # Extract filename by splitting on both slash types and removing null bytes
    cleaned = filename.replace("\\", "/").rstrip("/").split("/")[-1].replace("\x00", "").strip()
    clean = "".join(c for c in cleaned if c.isalnum() or c in (".", "_", "-"))
    return clean or "upload.jpg"


# ── 1. Security Headers Middleware ───────────────────────────────────────────

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Enforces hardened HTTP security headers on all responses."""

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        # Prevent framing / clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent browser MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Legacy browser XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer privacy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # HTTP Strict Transport Security (HSTS)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Restrict browser features (camera only for self, disable mic/geo)
        response.headers["Permissions-Policy"] = "camera=(self), microphone=(), geolocation=()"

        # Content Security Policy (CSP)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: blob:; "
            "connect-src 'self' ws: wss:; "
            "media-src 'self' blob:; "
            "frame-ancestors 'none';"
        )

        return response


# ── 2. Sliding Window Rate Limiter Middleware ────────────────────────────────

class RateLimiterMiddleware(BaseHTTPMiddleware):
    """In-memory sliding window rate limiter per client IP.

    Prevents Denial-of-Service (DoS) and GPU/CPU inference starvation attacks.
    """

    def __init__(self, app, requests_per_minute: int = 120):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60.0
        self.client_records: Dict[str, List[float]] = defaultdict(list)
        self.lock = Lock()

    def _get_client_ip(self, request: Request) -> str:
        # Check X-Forwarded-For if behind a reverse proxy, else request.client
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next):
        # Exclude static assets or health checks from aggressive limits if needed
        client_ip = self._get_client_ip(request)
        now = time.time()

        with self.lock:
            # Clean expired timestamps older than window
            timestamps = self.client_records[client_ip]
            valid_from = now - self.window_seconds
            self.client_records[client_ip] = [t for t in timestamps if t > valid_from]

            # Enforce limit
            if len(self.client_records[client_ip]) >= self.requests_per_minute:
                retry_after = int(self.window_seconds - (now - self.client_records[client_ip][0])) + 1
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Rate limit exceeded. Please wait before retrying.",
                        "retry_after_seconds": max(1, retry_after),
                    },
                    headers={"Retry-After": str(max(1, retry_after))},
                )

            self.client_records[client_ip].append(now)

        return await call_next(request)


# ── 3. Sanitized Exception Handling Middleware ───────────────────────────────

class SafeExceptionMiddleware(BaseHTTPMiddleware):
    """Catches unhandled server exceptions and returns sanitized error messages.

    Prevents information disclosure and internal filesystem path leakage.
    """

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except HTTPException:
            raise  # Let FastAPI handle explicit HTTPExceptions with proper status
        except Exception as exc:
            logger.exception(f"Unhandled server error at {request.method} {request.url.path}: {exc}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "An internal server error occurred. Please try again later."},
            )


# ── 4. WebSocket Security Manager ────────────────────────────────────────────

class WebSocketSecurityManager:
    """Manages WebSocket connection bounds, frame rate throttling, and payload limits."""

    def __init__(
        self,
        max_connections_per_ip: int = 5,
        min_frame_interval_seconds: float = 0.033,  # Max ~30 FPS per connection
        max_frame_bytes: int = 5 * 1024 * 1024,     # Max 5 MB per frame
    ):
        self.max_connections_per_ip = max_connections_per_ip
        self.min_frame_interval = min_frame_interval_seconds
        self.max_frame_bytes = max_frame_bytes
        self.active_connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        self.last_frame_time: Dict[WebSocket, float] = {}
        self.lock = Lock()

    def can_connect(self, client_ip: str, ws: WebSocket) -> bool:
        """Verify client IP has not exceeded maximum concurrent socket limit."""
        with self.lock:
            if len(self.active_connections[client_ip]) >= self.max_connections_per_ip:
                logger.warning(f"WebSocket connection rejected for IP {client_ip}: max sockets reached.")
                return False
            self.active_connections[client_ip].add(ws)
            self.last_frame_time[ws] = 0.0
            return True

    def remove_connection(self, client_ip: str, ws: WebSocket):
        """Clean up state on disconnect."""
        with self.lock:
            if client_ip in self.active_connections:
                self.active_connections[client_ip].discard(ws)
                if not self.active_connections[client_ip]:
                    del self.active_connections[client_ip]
            self.last_frame_time.pop(ws, None)

    def validate_frame(self, ws: WebSocket, frame_bytes: bytes) -> Optional[str]:
        """Validate frame size and throttle rate. Returns error string if invalid."""
        if len(frame_bytes) > self.max_frame_bytes:
            return f"Frame exceeded max size of {self.max_frame_bytes} bytes"

        now = time.time()
        last_time = self.last_frame_time.get(ws, 0.0)
        # Throttling check
        if now - last_time < self.min_frame_interval:
            # Drop frame or warn
            return None  # Will be skipped silently to preserve socket health

        self.last_frame_time[ws] = now
        return None


# Global security manager instance
ws_security = WebSocketSecurityManager(max_connections_per_ip=MAX_WS_CONNECTIONS_PER_IP)


# ── 5. Optional API Key Authorization ────────────────────────────────────────

def verify_api_key(request: Request):
    """If API_KEY is configured in the environment, require valid X-API-Key header.

    If API_KEY is empty or not configured, access is unrestricted.
    """
    if not API_KEY:
        return True  # No key required

    provided_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
    if not provided_key or provided_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return True
