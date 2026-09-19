# System Architecture — VisionAI

## 1. High-Level Architecture Overview

VisionAI is built as a lightweight, modular system separating presentation, API routing, machine learning inference, and model training.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        VisionAI Web Client (SPA)                       │
│     Vanilla HTML5 / CSS3 / ES6+  (Dashboard · Detect · Analytics)      │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │
                 ┌───────────────────┴───────────────────┐
                 │ HTTP (REST)                           │ WebSocket
                 ▼                                       ▼
    ┌──────────────────────────┐            ┌──────────────────────────┐
    │     POST /predict        │            │        /ws/live          │
    │  (FastAPI Router)        │            │  (FastAPI WebSocket)     │
    └────────────┬─────────────┘            └────────────┬─────────────┘
                 │                                       │
                 └───────────────────┬───────────────────┘
                                     ▼
                        ┌─────────────────────────┐
                        │      ObjectDetector     │
                        │    app/ml/inference.py  │
                        └────────────┬────────────┘
                                     ▼
                        ┌─────────────────────────┐
                        │      YOLOv8 Engine      │
                        │   (Ultralytics PyTorch) │
                        └────────────┬────────────┘
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼                                       ▼
        Structured JSON Results                 Real-time Box Coordinates
      { detections, annotated_b64 }               { detections, latency }
```

---

## 2. Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Frontend** | Vanilla JS, CSS3, HTML5 | Zero build steps, instant load time, maximum speed and responsiveness. |
| **Backend API** | FastAPI + Uvicorn | High performance, native async support, automated OpenAPI docs. |
| **ML Inference** | Ultralytics YOLOv8 Nano | State-of-the-art accuracy/speed tradeoff; runs on standard laptop CPU. |
| **Image Processing** | Pillow (PIL), NumPy | Fast decoding, RGB/BGR conversions, and coordinate transformations. |
| **Storage / State** | Browser `localStorage` | Client-side history and analytics without heavy external database servers. |
| **Testing** | `pytest`, `httpx` | Fast, deterministic API testing and validation coverage. |

---

## 3. Data Flow Pipelines

### A. Static Image Inference Flow (`POST /predict`)
1. User drops an image into the upload drop-zone.
2. Frontend sends a `multipart/form-data` request with the image file.
3. FastAPI validates content type against allowed MIME types and verifies payload size does not exceed `MAX_FILE_SIZE_MB`.
4. `app/ml/preprocessing.py` verifies image integrity and converts to RGB.
5. `ObjectDetector.detect()` runs YOLOv8 inference, calculates bounding boxes, confidence scores, and creates base64 annotated image.
6. Client receives response, stops the loading indicator, and renders the side-by-side inspection view.

### B. Decoupled Live WebSocket Streaming (`/ws/live`)
1. User activates webcam via browser `getUserMedia`.
2. HTML5 `<video>` element plays the local stream smoothly at 60 FPS.
3. An offscreen `<canvas>` captures periodic frames (compressed JPEG at quality 0.5) and streams binary data over `/ws/live`.
4. FastAPI WebSocket endpoint passes frame bytes to `ObjectDetector.detect_frame()`.
5. Backend computes boxes and sends lightweight coordinate telemetry `{ label, confidence, box: { xmin, ymin, xmax, ymax } }`.
6. Client overlays boxes onto an absolute canvas sitting atop the video feed — ensuring continuous 60 FPS visual smoothness regardless of network latency.

---

## 4. Directory & Module Boundaries

```
Object-Detection/
├── docs/                 # Architectural specifications & requirements
├── app/
│   ├── main.py           # FastAPI lifecycle management (lifespan hook)
│   ├── config.py         # Centralized configuration & environment loader
│   ├── schemas.py        # Pydantic input/output contracts
│   ├── api/
│   │   └── routes.py     # HTTP and WebSocket endpoint handlers
│   ├── ml/
│   │   ├── model.py      # Weights loader & PyTorch device mapping
│   │   ├── preprocessing.py # Image validation & tensor formatting
│   │   └── inference.py  # ObjectDetector service
│   └── templates/
│       └── index.html    # Single-Page Application presentation
├── tests/                # Automated pytest test suite
├── train.py              # Standalone rigorous YOLO training script
├── build_ui.py           # Programmatic UI compiler script
└── TRAINING.md           # Training execution manual
```

---

## 5. Architectural Rules
1. **Separation of Presentation & Business Logic**: UI templates never perform tensor operations or direct model inference.
2. **Stateless Request Handling**: The REST API does not store session cookies or server-side user state.
3. **Decoupled Video Frames**: Never send Base64-encoded annotated video frames over WebSocket; always send raw coordinate metadata to keep bandwidth ultra-low (< 50 KB/s).
4. **Early Validation**: Reject invalid files before allocating PyTorch tensors or decoding image bytes.
