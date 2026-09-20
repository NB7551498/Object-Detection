"""API Route definitions for the YOLO object detection web application."""

import base64
import os
from fastapi import APIRouter, File, HTTPException, Request, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, Response

from app.config import (
    CONFIDENCE_THRESHOLD,
    MODEL_NAME,
    MAX_FILE_SIZE_BYTES,
    MAX_FILE_SIZE_MB,
    DEVICE,
)
from app.ml.inference import ObjectDetector
from app.schemas import HealthResponse, ModelInfoResponse, DetectionResponse
from app.security import (
    sanitize_filename,
    validate_image_magic_bytes,
    verify_api_key,
    ws_security,
)

router = APIRouter()

# Global reference initialized during lifespan startup
detector: ObjectDetector = None


def init_detector():
    """Initialize the global ObjectDetector service."""
    global detector
    detector = ObjectDetector(
        model_name=MODEL_NAME,
        confidence_threshold=CONFIDENCE_THRESHOLD,
        device=DEVICE,
    )


# Allowed image upload formats
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp"}


@router.get("/", response_class=HTMLResponse, summary="VisionAI Web Client", tags=["frontend"])
@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
@router.get("/detect", response_class=HTMLResponse, include_in_schema=False)
@router.get("/history", response_class=HTMLResponse, include_in_schema=False)
@router.get("/analytics", response_class=HTMLResponse, include_in_schema=False)
@router.get("/models", response_class=HTMLResponse, include_in_schema=False)
@router.get("/settings", response_class=HTMLResponse, include_in_schema=False)
async def get_frontend():
    """Serve the interactive web client frontend."""
    template_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "templates", "index.html"
    )
    if not os.path.exists(template_path):
        raise HTTPException(status_code=500, detail="Frontend HTML template not found.")

    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@router.get("/favicon.ico", include_in_schema=False)
async def get_favicon():
    """Return an empty 204 No Content for favicon requests to prevent 404 logs."""
    return Response(status_code=204)



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
        max_file_size_mb=MAX_FILE_SIZE_MB,
    )


@router.post(
    "/predict",
    response_model=DetectionResponse,
    summary="Run object detection on image",
    tags=["inference"],
)
async def predict_endpoint(
    request: Request,
    file: UploadFile = File(..., description="Image file to detect (JPEG, PNG, WebP, BMP)"),
):
    """Accept an uploaded image, run YOLO object detection, and return boxes and labels.

    The response includes a structured list of detected objects (with bounding boxes
    and confidence scores) along with a base64-encoded JPEG image of the annotated results.

    **Accepted formats**: JPEG, PNG, WebP, BMP  
    **Max file size**: 15 MB
    """
    # ── Verify optional API Key ──────────────────────────────────
    verify_api_key(request)

    # ── Validate content type header ─────────────────────────────
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type: '{file.content_type}'. "
                f"Accepted types: {', '.join(sorted(ALLOWED_CONTENT_TYPES))}."
            ),
        )

    # ── Read and validate payload size ───────────────────────────
    image_bytes = await file.read()
    if len(image_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({len(image_bytes)} bytes). Maximum is {MAX_FILE_SIZE_BYTES} bytes.",
        )

    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # ── Validate binary image magic signature (Anti-MIME spoofing) ─
    if not validate_image_magic_bytes(image_bytes, file.content_type):
        raise HTTPException(
            status_code=400,
            detail="File content does not match genuine image binary signature.",
        )

    # ── Inference ────────────────────────────────────────────────
    try:
        detections, annotated_image_b64 = detector.detect(image_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Object detection failed during model execution.",
        )

    # ── Build response ───────────────────────────────────────────
    return DetectionResponse(
        detections=detections,
        annotated_image=annotated_image_b64,
    )


@router.websocket("/ws/live")
async def websocket_live_detection(websocket: WebSocket):
    """WebSocket endpoint for real-time live webcam object detection.

    Receives camera video frames from the browser client, throttles frame rate,
    runs low-latency YOLO inference, and streams back detection results.
    """
    client_ip = websocket.client.host if websocket.client else "unknown"

    # Enforce maximum concurrent active sockets per IP
    if not ws_security.can_connect(client_ip, websocket):
        await websocket.close(code=1008, reason="Max concurrent connections reached.")
        return

    await websocket.accept()
    try:
        while True:
            message = await websocket.receive()
            frame_bytes = None

            if "bytes" in message and message["bytes"]:
                frame_bytes = message["bytes"]
            elif "text" in message and message["text"]:
                text_data = message["text"]
                if "," in text_data:
                    text_data = text_data.split(",", 1)[1]
                frame_bytes = base64.b64decode(text_data)

            if not frame_bytes:
                continue

            # Frame size validation & rate throttling
            err = ws_security.validate_frame(websocket, frame_bytes)
            if err:
                await websocket.send_json({"error": err, "detections": []})
                continue

            try:
                result = detector.detect_frame(frame_bytes)
                await websocket.send_json(result)
            except Exception:
                await websocket.send_json({"error": "Detection error", "detections": []})

    except WebSocketDisconnect:
        pass
    except Exception:
        try:
            await websocket.close()
        except Exception:
            pass
    finally:
        ws_security.remove_connection(client_ip, websocket)

