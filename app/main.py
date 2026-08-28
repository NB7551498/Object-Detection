"""FastAPI application for Object Detection.

Serves an interactive Gemini-style web frontend at the root route `/` and exposes
`/predict` and `/health` endpoints for automated and manual model consumption.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse

from app.model import load_model, predict
from app.preprocessing import preprocess_image
from app.schemas import HealthResponse, DetectionResponse

# ── Configuration ────────────────────────────────────────────────────
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp"}
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB

# ── Global model reference (set during lifespan) ────────────────────
_model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the model into memory at startup; release on shutdown."""
    global _model
    print("Loading pre-trained Faster R-CNN ResNet-50 object detection model...")
    try:
        _model = load_model()
        print("Model loaded successfully.")
    except Exception as exc:
        print(f"ERROR: Failed to load detection model: {exc}")
        raise
    yield
    _model = None
    print("Model unloaded.")


# ── App instance ─────────────────────────────────────────────────────
app = FastAPI(
    title="Object Detection API",
    description=(
        "A lightweight REST API and web UI that performs object detection "
        "using Faster R-CNN ResNet-50 v2. Part of the internSpark program (Task 3 of 4)."
    ),
    version="2.0.0",
    lifespan=lifespan,
)


# ── Endpoints ────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse, summary="Gemini-style Chat UI", tags=["frontend"])
async def get_frontend():
    """Serve the interactive web client frontend at the root route."""
    template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    if not os.path.exists(template_path):
        raise HTTPException(status_code=500, detail="Frontend HTML template not found.")
    
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@app.get(
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


@app.post(
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
    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({len(image_bytes)} bytes). Maximum is {MAX_FILE_SIZE} bytes.",
        )

    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # ── Preprocess ───────────────────────────────────────────────
    try:
        pil_image, input_tensor = preprocess_image(image_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # ── Inference ────────────────────────────────────────────────
    try:
        detections, annotated_image_b64 = predict(_model, pil_image, input_tensor, confidence_threshold=0.5)
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
