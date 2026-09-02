# 👁️ YOLOv8 Live Object Detection & Gemini-Style Web UI

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.13-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00FFFF.svg?logo=yolo&logoColor=black)](https://docs.ultralytics.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.6.0-EE4C2C.svg?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Tests](https://img.shields.io/badge/Tests-8%20Passed-brightgreen.svg)](https://pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An end-to-end, production-oriented **Object Detection application** powered by **Ultralytics YOLOv8** (`yolov8n.pt`, 80 COCO categories). Features a dark-themed chat frontend styled like the **Gemini web client** with seamless **real-time live webcam streaming over WebSocket**.

---

## 📑 Table of Contents

- [🌟 Key Highlights](#-key-highlights)
- [🏗️ System Architecture](#️-system-architecture)
- [🖥️ Frontend Interface Modes](#️-frontend-interface-modes)
- [📁 Project Layout](#-project-layout)
- [⚡ Quick Start Guide](#-quick-start-guide)
  - [Prerequisites](#prerequisites)
  - [Local Installation (Windows / Linux / macOS)](#local-installation-windows--linux--macos)
  - [Running from VS Code](#running-from-vs-code)
- [📹 Live Camera Streaming (WebSocket)](#-live-camera-streaming-websocket)
- [🔌 REST & WebSocket API Reference](#-rest--websocket-api-reference)
  - [API Endpoints Overview](#api-endpoints-overview)
  - [cURL Request Example](#curl-request-example)
  - [Python Client Example](#python-client-example)
  - [WebSocket Frame Streaming Protocol](#websocket-frame-streaming-protocol)
- [📊 Benchmarks & Performance](#-benchmarks--performance)
- [🧪 Automated Testing](#-automated-testing)
- [⚙️ Environment Variables](#️-environment-variables)
- [📄 License](#-license)

---

## 🌟 Key Highlights

- **Ultralytics YOLOv8 Integration**: Employs YOLOv8 Nano (`yolov8n.pt`, ~6.2 MB weights) for high-precision inference across 80 COCO classes with rapid CPU inference times (~15–50 ms).
- **Dual-Mode Gemini UI**:
  - 💬 **Image Upload & Chat**: Upload static photos (JPEG, PNG, WebP, BMP) with drag-and-drop, bounding-box annotations, confidence scoring, and tabular metadata analysis.
  - 📹 **Live Camera Viewfinder**: Access your device's webcam directly in the browser via HTML5 `getUserMedia` and stream frames in real time.
- **Low-Latency WebSocket Streaming**: Bidirectional `/ws/live` channel streaming video frames and returning detection overlays with a live FPS meter and latency HUD.
- **Production Modular Layout**: Strict separation of concerns across Configuration (`config.py`), Models (`app/ml/model.py`), Preprocessing (`app/ml/preprocessing.py`), Inference Service (`app/ml/inference.py`), and Routes (`app/api/routes.py`).
- **Comprehensive Test Suite**: Automated unit and integration testing via `pytest` and `httpx` with 100% passing test coverage on health, validations, and tensor pipelines.

---

## 🏗️ System Architecture

```
                             ┌─────────────────────────────────────────┐
                             │       Gemini-Style Web Client           │
                             │   (Image Upload Chat + Live Camera)     │
                             └───────────────────┬─────────────────────┘
                                                 │
                   ┌─────────────────────────────┴─────────────────────────────┐
                   │ (HTTP POST /predict)                                      │ (WebSocket /ws/live)
                   ▼                                                           ▼
       ┌───────────────────────┐                                   ┌───────────────────────┐
       │   FastAPI REST API    │                                   │  FastAPI WebSocket    │
       └───────────┬───────────┘                                   └───────────┬───────────┘
                   │                                                           │
                   └─────────────────────────────┬─────────────────────────────┘
                                                 ▼
                                    ┌─────────────────────────┐
                                    │     ObjectDetector      │
                                    │    (app/ml/inference)   │
                                    └────────────┬────────────┘
                                                 │
                                                 ▼
                                    ┌─────────────────────────┐
                                    │    YOLOv8 Engine        │
                                    │     (yolov8n.pt)        │
                                    └────────────┬────────────┘
                                                 │
                       ┌─────────────────────────┴─────────────────────────┐
                       ▼                                                   ▼
             Structured Predictions                                Annotated Images
             - Class Label (e.g. 'car')                            - Real-time Video Stream
             - Confidence Score (90.2%)                            - Base64 JPEG with Boxes
             - Coordinates [xmin, ymin, xmax, ymax]
```

---

## 🖥️ Frontend Interface Modes

### 1. 💬 Image Upload Chat Mode
- Drag and drop or upload any local image file (up to 15 MB).
- Image is rendered in a Gemini-style user message bubble.
- YOLOv8 generates an annotated image with colored bounding boxes and a structured analysis table indicating detected class, confidence score badge, and bounding box coordinates.

### 2. 📹 Real-Time Live Camera Mode
- Direct browser access to your device's webcam.
- Live canvas displaying real-time bounding boxes and labels.
- **Heads-Up Display (HUD)**:
  - 🔴 **LIVE** indicator badge.
  - ⚡ **FPS Meter** displaying live frames per second.
  - ⏱️ **Latency Chip** showing model inference time per frame in milliseconds.
  - 🎯 **Dynamic Pill Badges** showing active detected objects in the viewfinder.

---

## 📁 Project Layout

```
Object-Detection/
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions automated test workflow
├── .vscode/
│   ├── launch.json            # One-click VS Code Run & Debug configuration
│   └── settings.json          # VS Code pytest discovery settings
├── app/
│   ├── __init__.py            # Package initialization
│   ├── main.py                # FastAPI app initialization and lifespan context
│   ├── config.py              # Environment variable configurations
│   ├── schemas.py             # Pydantic data schemas
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py          # REST & WebSocket endpoints (/predict, /ws/live, /health)
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── model.py           # YOLOv8 weights loading module
│   │   ├── preprocessing.py   # Image to PIL & PyTorch tensor conversion
│   │   └── inference.py       # ObjectDetector inference & visualization wrapper
│   └── templates/
│       └── index.html         # Gemini-style responsive HTML5/CSS/JS frontend
├── tests/
│   ├── __init__.py            # Test suite package
│   ├── test_health.py         # Liveness and metadata tests
│   ├── test_validation.py     # File format and size limit tests
│   └── test_model.py          # Tensor shape, inference, and frame detection tests
├── .gitignore                 # Excludes caches, venvs, and *.pt weights
├── requirements.txt           # Version-pinned Python dependencies
├── yolov8n.pt                 # YOLOv8 Nano model weights
└── README.md                  # Project documentation
```

---

## ⚡ Quick Start Guide

### Prerequisites
- **Python 3.11+** or **Python 3.13+**
- **pip** package manager
- A modern web browser with webcam access (Chrome, Edge, Firefox, Safari)

### Local Installation (Windows / Linux / macOS)

```bash
# 1. Clone the repository
git clone https://github.com/NB7551498/Object-Detection.git
cd Object-Detection

# 2. Create and activate virtual environment
# Windows (PowerShell):
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS:
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the application
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Once running:
- **Interactive UI**: [http://localhost:8000/](http://localhost:8000/)
- **Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Specification**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Running from VS Code
1. Open the project folder in **VS Code**.
2. Press `Ctrl + Shift + D` to open the **Run & Debug** menu.
3. Select **"FastAPI: Run/Debug Object Detection API"** and press `F5`.
4. The server will launch in your debug console with hot reload enabled.

---

## 📹 Live Camera Streaming (WebSocket)

1. Navigate to **[http://localhost:8000/](http://localhost:8000/)**.
2. In the top header bar, click the **"Live Camera"** tab button.
3. Click the **"Start Camera"** button and grant browser webcam permission.
4. Frames are captured via an offscreen canvas, sent over WebSocket (`/ws/live`), processed by YOLOv8, and streamed back with bounding boxes at ~20+ FPS.

---

## 🔌 REST & WebSocket API Reference

### API Endpoints Overview

| Method | Path | Description | Response Model |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Serves the Gemini-style web client | HTML Document |
| `GET` | `/health` | Liveness health probe | `{"status": "ok"}` |
| `GET` | `/model-info` | Active model configurations & compute device | `ModelInfoResponse` |
| `POST` | `/predict` | Static image object detection inference | `DetectionResponse` |
| `WS` | `/ws/live` | Real-time bidirectional camera frame detection | JSON detection frame |

---

### cURL Request Example

Detect objects in any image file:

```bash
curl -X POST "http://localhost:8000/predict" \
     -H "accept: application/json" \
     -F "file=@path/to/your/image.jpg"
```

**Example JSON Response**:

```json
{
  "detections": [
    {
      "label": "car",
      "confidence": 0.9412,
      "box": {
        "xmin": 75.3,
        "ymin": 312.7,
        "xmax": 931.5,
        "ymax": 530.3
      }
    }
  ],
  "annotated_image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

---

### Python Client Example

```python
import requests

url = "http://localhost:8000/predict"
image_path = "sample.jpg"

with open(image_path, "rb") as f:
    response = requests.post(url, files={"file": ("image.jpg", f, "image/jpeg")})

data = response.json()
print(f"Detected {len(data['detections'])} objects:")
for item in data["detections"]:
    print(f" - {item['label']} ({item['confidence'] * 100:.1f}%) at {item['box']}")
```

---

### WebSocket Frame Streaming Protocol

Connect via JavaScript:

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/live");

ws.onopen = () => {
    console.log("Connected to YOLO live stream");
    // Send binary JPEG blob from HTML5 Canvas
    canvas.toBlob((blob) => ws.send(blob), 'image/jpeg', 0.7);
};

ws.onmessage = (event) => {
    const result = JSON.parse(event.data);
    console.log(`Latency: ${result.inference_time_ms} ms`);
    console.log(`Detections:`, result.detections);
    
    // Display annotated frame
    imgElement.src = result.annotated_image;
};
```

---

## 📊 Benchmarks & Performance

Measured on a standard Intel Core i7 CPU (without dedicated GPU):

| Metric | Measurement | Notes |
| :--- | :--- | :--- |
| **Model Size** | ~6.2 MB (`yolov8n.pt`) | Ultra-lightweight memory footprint |
| **Inference Latency** | 15 – 45 ms | Optimized PyTorch CPU execution |
| **Live Stream FPS** | 18 – 30 FPS | WebSocket stream on 640×480 resolution |
| **RAM Utilization** | ~180 MB | Lean FastAPI + Torch runtime |
| **Cold Start Startup** | < 2.5 seconds | Automatic model caching |

---

## 🧪 Automated Testing

The project includes unit, validation, and integration tests built with **pytest** and **httpx**:

```bash
# Run tests locally
pytest -v
```

**Test Execution Results**:
```
tests/test_health.py::test_health_check PASSED                   [ 12%]
tests/test_health.py::test_model_info PASSED                     [ 25%]
tests/test_model.py::test_preprocessing PASSED                   [ 37%]
tests/test_model.py::test_object_detector_inference PASSED       [ 50%]
tests/test_model.py::test_object_detector_frame_detection PASSED [ 62%]
tests/test_validation.py::test_predict_invalid_content_type PASSED [ 75%]
tests/test_validation.py::test_predict_empty_file PASSED         [ 87%]
tests/test_validation.py::test_predict_oversized_file PASSED     [100%]

======================= 8 passed in 17.93s ========================
```

---

## ⚙️ Environment Variables

Configure application behavior using environment variables:

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `CONFIDENCE_THRESHOLD` | `float` | `0.5` | Minimum confidence score to retain detection (0.0 – 1.0) |
| `MODEL_NAME` | `str` | `yolov8n.pt` | YOLO weights path or identifier (`yolov8n.pt`, `yolov8s.pt`, etc.) |
| `MAX_FILE_SIZE_MB` | `int` | `15` | Maximum allowed image upload size in Megabytes |
| `DEVICE` | `str` | `auto` | Execution compute target (`cpu` or `cuda`) |

---

## 📄 License

Distributed under the [MIT License](LICENSE).
