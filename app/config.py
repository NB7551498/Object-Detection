"""App configuration management using environment variables."""

import os
import torch

# Confidence threshold to filter weak detections
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))

# Underlyng model name (e.g., fasterrcnn_resnet50_fpn_v2)
MODEL_NAME = os.getenv("MODEL_NAME", "fasterrcnn_resnet50_fpn_v2")

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
API_TITLE = "Object Detection API"
API_VERSION = "2.0.0"
API_DESCRIPTION = (
    "A production-ready modular REST API and web UI that performs object "
    "detection using Faster R-CNN. Part of the internSpark program (Task 3 of 4)."
)
