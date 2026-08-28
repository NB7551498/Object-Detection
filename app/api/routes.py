"""API Route definitions for the object detection web application."""

import os
from fastapi import APIRouter, File, HTTPException, UploadFile, Request
from fastapi.responses import HTMLResponse

from app.config import (
    CONFIDENCE_THRESHOLD,
    MODEL_NAME,
    MAX_FILE_SIZE_BYTES,
    MAX_FILE_SIZE_MB,
    DEVICE,
)
from app.ml.inference import ObjectDetector
from app.schemas import HealthResponse, ModelInfoResponse, DetectionResponse

router = APIRouter()

# Global reference initialized during lifespan startup
detector: ObjectDetector = None


def init_detector():
    """Initialize the global ObjectDetector service."""
    global detector
    detector = ObjectDetector(
        confidence_threshold=CONFIDENCE_THRESHOLD,
        device=DEVICE
    )


# Allowed image upload formats
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp"}


@router.get("/", response_class=HTMLResponse, summary="Gemini-style Chat UI", tags=["frontend"])
async def get_frontend():
    """Serve the interactive web client frontend at the root route."""
    template_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "templates", "index.html"
    )
    if not os.path.exists(template_path):
        raise HTTPException(status_code=500, detail="Frontend HTML template not found.")

    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    tags=["status"],
)
async def health_check():
    """Return API health status.

    Use this endpoint for liveness probes or uptime monitoring.
    """
    return HealthResponse(status="ok")


@router.get(
    "/model-info",
    response_model=ModelInfoResponse,
    summary="Model metadata details",
    tags=["status"],
)
async def get_model_info():
    """Expose details about the active model configuration and execution device."""
    return ModelInfoResponse(
        model=MODEL_NAME,
        device=DEVICE,
        confidence_threshold=CONFIDENCE_THRESHOLD,
        max_file_size_mb=MAX_FILE_SIZE_MB
    )


@router.post(
    "/predict",
    response_model=DetectionResponse,
    summary="Run object detection",
    tags=["inference"],
)
async def predict_endpoint(file: UploadFile = File(..., description="Image file to detect (JPEG, PNG, WebP, BMP)")):
    """Accept an uploaded image, run object detection, and return boxes and labels.

    The response includes a structured list of detected objects (with bounding boxes
    and confidence scores) along with a base64-encoded JPEG image of the annotated results.

    **Accepted formats**: JPEG, PNG, WebP, BMP  
    **Max file size**: 15 MB
    """
    # ── Validate content type ────────────────────────────────────
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type: '{file.content_type}'. "
                f"Accepted types: {', '.join(sorted(ALLOWED_CONTENT_TYPES))}."
            ),
        )

    # ── Read and validate size ───────────────────────────────────
    image_bytes = await file.read()
    if len(image_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({len(image_bytes)} bytes). Maximum is {MAX_FILE_SIZE_BYTES} bytes.",
        )

    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # ── Inference ────────────────────────────────────────────────
    try:
        detections, annotated_image_b64 = detector.detect(image_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Object detection failed: {exc}",
        )

    # ── Build response ───────────────────────────────────────────
    return DetectionResponse(
        detections=detections,
        annotated_image=annotated_image_b64
    )
