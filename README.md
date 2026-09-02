# YOLOv8 Object Detection API & Gemini-style Live Camera UI

A high-performance, production-ready **Object Detection** service powered by **Ultralytics YOLOv8** (`yolov8n.pt`, 80 COCO categories) with a responsive chat frontend styled like the **Gemini web client** and **real-time live webcam streaming via WebSocket**.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Project Architecture](#project-architecture)
- [Project Structure](#project-structure)
- [Quick Start — Local](#quick-start--local)
- [Live Webcam Streaming](#live-webcam-streaming)
- [API Endpoints & WebSocket](#api-endpoints--websocket)
- [Automated Testing](#automated-testing)
- [Configuration](#configuration)

---

## Overview

This project provides end-to-end computer vision capabilities through both standard REST APIs and real-time WebSockets:

- **Ultralytics YOLOv8 Nano** (`yolov8n.pt`): Ultra-fast (~15–60ms on CPU, <5ms on GPU) object detection across 80 COCO classes.
- **Real-time Live Webcam Streaming**: Stream frames from your browser directly to FastAPI over a low-latency bidirectional WebSocket connection (`/ws/live`).
- **Gemini-Style Web UI**: Switch seamlessly between **Image Upload Chat** and **Live Camera** mode with real-time FPS counter, inference latency HUD, and detected object badges.
- **REST Inference Endpoint** (`POST /predict`): Upload any image (JPEG, PNG, WebP, BMP) to receive structured bounding boxes, confidence scores, and annotated visualizations.
- **Automated Test Suite**: Comprehensive tests using `pytest` verifying health probes, file validation, tensor shapes, and frame detection.

---

## Project Architecture

```
                       ┌───────────────────────────────┐
                       │     Gemini-Style Web UI       │
                       │   (Chat & Live Camera View)   │
                       └──────────────┬────────────────┘
                                      │
               ┌──────────────────────┴──────────────────────┐
               │ (HTTP /predict)                             │ (WebSocket /ws/live)
               ▼                                             ▼
       ┌───────────────┐                             ┌───────────────┐
       │ FastAPI REST  │                             │ FastAPI WS    │
       └───────┬───────┘                             └───────┬───────┘
               │                                             │
               └──────────────────────┬──────────────────────┘
                                      ▼
                             ┌─────────────────┐
                             │ ObjectDetector  │
                             │  (app/ml/...)   │
                             └────────┬────────┘
                                      │
                                      ▼
                             ┌─────────────────┐
                             │  YOLOv8 Engine  │
                             │  (yolov8n.pt)   │
                             └────────┬────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
             Structured Detections               Annotated Image
             [box, class, score]               (Live Video / Base64)
```

---

## Project Structure

```
model-detection/
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI workflow
├── app/
│   ├── __init__.py           # Package marker
│   ├── main.py               # FastAPI entrypoint & lifespan management
│   ├── config.py             # Environment variable configuration loading
│   ├── schemas.py            # Pydantic schemas (Request/Response validation)
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py         # HTTP & WebSocket route definitions
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── model.py          # YOLOv8 initialization onto CPU/GPU
│   │   ├── preprocessing.py  # Image-to-tensor & PIL conversions
│   │   └── inference.py      # ObjectDetector runner & real-time frame annotation
│   └── templates/
│       └── index.html        # Gemini-style Web UI (Image Chat + Live Camera)
├── tests/
│   ├── __init__.py           # Package marker
│   ├── test_health.py        # API health and model metadata tests
│   ├── test_validation.py    # Payload size and format validation tests
│   └── test_model.py         # YOLO inference and frame detection tests
├── requirements.txt          # Pinned dependencies
├── yolov8n.pt                # YOLOv8 Nano model weights
└── README.md                 # Project documentation
```

---

## Quick Start — Local

### 1. Activate Environment & Install Dependencies

```bash
# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the Server

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

- Open **[http://localhost:8000/](http://localhost:8000/)** to access the interactive Gemini UI.
- Open **[http://localhost:8000/docs](http://localhost:8000/docs)** to view the interactive OpenAPI documentation.

---

## Live Webcam Streaming

1. Open `http://localhost:8000/` in Chrome, Firefox, or Edge.
2. Click on the **"Live Camera"** tab in the top header.
3. Click the **"Start Camera"** button and allow camera permission.
4. The system will stream your webcam video frames over WebSocket to the YOLO backend, drawing bounding boxes and labels with a live FPS meter and detection counter in real time!

---

## API Endpoints & WebSocket

### `GET /`
Serves the Gemini-style dual-mode frontend.

### `GET /health`
Returns `{"status": "ok"}` for uptime verification.

### `GET /model-info`
Returns active configuration parameters:
```json
{
  "model": "yolov8n.pt",
  "device": "cpu",
  "confidence_threshold": 0.5,
  "max_file_size_mb": 15
}
```

### `POST /predict`
Upload an image to run YOLO object detection.
- **Request**: `multipart/form-data` with `file` field. (JPEG, PNG, WebP, BMP | Max: 15 MB)
- **Response**:
```json
{
  "detections": [
    {
      "label": "person",
      "confidence": 0.9234,
      "box": {
        "xmin": 45.2,
        "ymin": 88.0,
        "xmax": 210.5,
        "ymax": 450.1
      }
    }
  ],
  "annotated_image": "data:image/jpeg;base64,..."
}
```

### `WebSocket /ws/live`
Bidirectional WebSocket stream for real-time video frames.
- **Client sends**: Binary JPEG blob or Base64 string.
- **Server returns**:
```json
{
  "detections": [...],
  "annotated_image": "data:image/jpeg;base64,...",
  "inference_time_ms": 18.5
}
```

---

## Automated Testing

To run the complete test suite locally:

```bash
pytest
```

**Result**:
```
tests\test_health.py ..                                                  [ 25%]
tests\test_model.py ...                                                  [ 62%]
tests\test_validation.py ...                                             [100%]
======================= 8 passed in 17.93s ========================
```

---

## Configuration

Configure the application via environment variables (with safe defaults):

| Environment Variable | Default | Description |
| -------------------- | ------- | ----------- |
| `CONFIDENCE_THRESHOLD`| `0.5` | Minimum score to retain detection |
| `MODEL_NAME`         | `yolov8n.pt` | YOLO model weights (e.g. `yolov8n.pt`, `yolov8s.pt`, `yolo11n.pt`) |
| `MAX_FILE_SIZE_MB`   | `15` | Maximum upload size in Megabytes |
| `DEVICE`             | auto-detected | Compute target (`cpu` or `cuda`) |
