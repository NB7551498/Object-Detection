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
