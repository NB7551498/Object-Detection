"""App configuration management using environment variables."""

import os
import torch

# Confidence threshold to filter weak detections
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))

# Underlying YOLO model name (e.g., yolov8n.pt, yolov8s.pt, yolo11n.pt)
MODEL_NAME = os.getenv("MODEL_NAME", "yolov8n.pt")

# Maximum upload file size in Megabytes
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "15"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Active compute device for inference
# Uses GPU if available, falls back to CPU
DEVICE = os.getenv(
    "DEVICE",
    "cuda" if torch.cuda.is_available() else "cpu"
)

# API Metadata configuration
API_TITLE = "YOLOv8 Object Detection & Live Webcam API"
API_VERSION = "3.0.0"
API_DESCRIPTION = (
    "A production-ready modular REST and WebSocket API with real-time live "
    "webcam streaming powered by Ultralytics YOLOv8."
)

# ── Security Configuration ───────────────────────────────────────────
# In-memory sliding window rate limiting (requests per minute per client IP)
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))

# Allowed CORS origins
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",")
    if origin.strip()
]

# Max concurrent WebSocket streams per IP address
MAX_WS_CONNECTIONS_PER_IP = int(os.getenv("MAX_WS_CONNECTIONS_PER_IP", "5"))

# Maximum allowable image width/height in pixels to block decompression bombs
MAX_IMAGE_DIMENSION = int(os.getenv("MAX_IMAGE_DIMENSION", "8192"))

# Optional secret API key; if set, required on /predict via X-API-Key header
API_KEY = os.getenv("API_KEY", "").strip()

