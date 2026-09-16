# VisionAI — Intelligent Object Detection

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.13-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00FFFF.svg)](https://docs.ultralytics.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.6.0-EE4C2C.svg?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Tests](https://img.shields.io/badge/Tests-8%20Passed-brightgreen.svg)](https://pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A production-quality **AI computer vision application** powered by **Ultralytics YOLOv8**. Features a fully redesigned dark-first **VisionAI** interface with sidebar navigation, real-time live camera detection, detection history, analytics, model info, and a rigorous training pipeline — all running on a lightweight FastAPI backend.

---

## 📑 Table of Contents

- [🌟 Key Highlights](#-key-highlights)
- [🖥️ UI Overview](#️-ui-overview)
- [🏗️ System Architecture](#️-system-architecture)
- [📁 Project Layout](#-project-layout)
- [⚡ Quick Start](#-quick-start)
- [🎯 Training Your Own Model](#-training-your-own-model)
- [🔌 API Reference](#-api-reference)
- [📊 Benchmarks](#-benchmarks)
- [🧪 Testing](#-testing)
- [⚙️ Environment Variables](#️-environment-variables)
- [📄 License](#-license)

---

## 🌟 Key Highlights

- **VisionAI SPA** — Professional dark-first UI with sidebar navigation (Dashboard, Detect, History, Analytics, Models, Settings). Responsive on desktop, tablet, and mobile.
- **YOLOv8 Backend** — `yolov8n.pt` (80 COCO classes, ~6.2 MB) serving `/predict` REST and `/ws/live` WebSocket endpoints.
- **Decoupled Live Rendering** — Frontend renders the webcam feed natively at 60+ FPS; YOLO inference results stream asynchronously over WebSocket without blocking the video.
- **Rigorous Training Pipeline** — `train.py` with full augmentation (mosaic, MixUp, copy-paste, HSV jitter), AdamW optimizer, cosine LR, early stopping, post-training eval, and auto export.
- **Detection History & Analytics** — All sessions stored in `localStorage`. Class distribution bar chart, per-session mAP stats, and relative timestamps built in.
- **Production Layout** — Strict separation: config, schemas, ML pipeline, routes, and frontend are all independent modules.
- **Full Test Suite** — 8 automated pytest tests covering health, validation, preprocessing, inference, and frame detection.

---

## 🖥️ UI Overview

The VisionAI interface is a single-page application with the following views:

| View | What it does |
|---|---|
| **Dashboard** | Total runs, objects found, avg confidence, active model, recent detection feed |
| **Detect → Image** | Drag-and-drop upload zone with step-by-step processing state and two-column results (annotated image + confidence bar table) |
| **Detect → Live Camera** | Real-time webcam detection with FPS/latency/object HUD overlay |
| **History** | Full session log with object count, confidence badge, and relative timestamps |
| **Analytics** | Class distribution bar chart and session summary — built from real detection data |
| **Models** | Active model details: device, confidence threshold, class count, status |
| **Settings** | Read-only backend config: weights, device, threshold, max upload size |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────┐
│              VisionAI Web Client (SPA)           │
│  Dashboard · Detect · History · Analytics · ...  │
└──────────────────────┬──────────────────────────┘
                       │
         ┌─────────────┴──────────────┐
         │ HTTP POST /predict         │ WebSocket /ws/live
         ▼                            ▼
┌────────────────┐          ┌────────────────────┐
│ FastAPI REST   │          │  FastAPI WebSocket  │
└───────┬────────┘          └────────┬────────────┘
        │                           │
        └─────────────┬─────────────┘
                      ▼
          ┌───────────────────────┐
          │    ObjectDetector     │
          │   app/ml/inference    │
          └──────────┬────────────┘
                     ▼
          ┌───────────────────────┐
          │    YOLOv8 Engine      │
          │     yolov8n.pt        │
          └──────────┬────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
Structured Detections      Annotated Image
{ label, confidence, box }  Base64 JPEG (REST only)
```

---

## 📁 Project Layout

```
Object-Detection/
├── app/
│   ├── main.py              # FastAPI app + lifespan startup
│   ├── config.py            # Env variable config
│   ├── schemas.py           # Pydantic response models
│   ├── api/
│   │   └── routes.py        # /predict  /ws/live  /health  /model-info
│   ├── ml/
│   │   ├── model.py         # YOLOv8 weights loader
│   │   ├── preprocessing.py # PIL image normalisation
│   │   └── inference.py     # ObjectDetector (detect + detect_frame)
│   └── templates/
│       └── index.html       # VisionAI SPA (Vanilla JS, no frameworks)
├── tests/
│   ├── test_health.py       # Health + model-info tests
│   ├── test_validation.py   # Format/size validation tests
│   └── test_model.py        # Inference + frame detection tests
├── train.py                 # Rigorous YOLOv8 training pipeline
├── build_ui.py              # UI builder — regenerates index.html
├── TRAINING.md              # Full training guide
├── requirements.txt
├── yolov8n.pt               # Pre-trained weights
└── README.md
```

---

## ⚡ Quick Start

### Prerequisites

- Python 3.11+
- pip
- Modern browser with webcam (Chrome, Edge, Firefox)

### Installation

```bash
# 1. Clone
git clone https://github.com/NB7551498/Object-Detection.git
cd Object-Detection

# 2. Virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate

# Linux / macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
pip install matplotlib opencv-python psutil polars ultralytics-thop

# 4. Start the server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open **[http://localhost:8000](http://localhost:8000)** — the VisionAI UI loads immediately.

| URL | Purpose |
|---|---|
| `http://localhost:8000/` | VisionAI UI |
| `http://localhost:8000/docs` | Swagger API docs |
| `http://localhost:8000/redoc` | ReDoc API spec |

### VS Code

1. Open project in VS Code.
2. `Ctrl+Shift+D` → select **"FastAPI: Run/Debug Object Detection API"** → `F5`.

---

## 🎯 Training Your Own Model

See **[TRAINING.md](TRAINING.md)** for the full guide. Quick commands:

```bash
# Smoke test — trains on COCO128 (auto-downloads), 50 epochs
python train.py

# Custom dataset
python train.py --dataset data/my_dataset.yaml --model yolov8s.pt --epochs 150

# GPU run
python train.py --model yolov8m.pt --epochs 200 --batch 32 --device cuda
```

### What `train.py` does

| Stage | Detail |
|---|---|
| **Augmentation** | Mosaic, MixUp 0.1, copy-paste, HSV jitter, rotation ±10°, scale ±0.5 |
| **Optimizer** | AdamW · lr0=0.001 · cosine decay · 3-epoch warmup |
| **Early stopping** | Stops after 15 epochs without mAP improvement |
| **Evaluation** | Auto-runs `model.val()` — prints mAP50, mAP50-95, Precision, Recall |
| **Export** | Copies `best.pt` → `trained_model.pt` at repo root for the API |

### Using trained weights with the API

```bash
# Set env var and restart server
set MODEL_NAME=trained_model.pt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Model size guide

| Model | Params | mAP50-95 | Best for |
|---|---|---|---|
| `yolov8n.pt` | 3.2 M | 37.3 | CPU / demo |
| `yolov8s.pt` | 11.2 M | 44.9 | Balanced |
| `yolov8m.pt` | 25.9 M | 50.2 | GPU production |
| `yolov8l.pt` | 43.7 M | 52.9 | High accuracy |

---

## 🔌 API Reference

### Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | VisionAI web UI |
| `GET` | `/health` | Liveness probe → `{"status":"ok"}` |
| `GET` | `/model-info` | Active model config |
| `POST` | `/predict` | Image object detection |
| `WS` | `/ws/live` | Real-time frame detection |

### POST `/predict`

```bash
curl -X POST "http://localhost:8000/predict" \
     -F "file=@image.jpg"
```

```json
{
  "detections": [
    {
      "label": "person",
      "confidence": 0.9412,
      "box": { "xmin": 75.3, "ymin": 120.1, "xmax": 310.5, "ymax": 480.2 }
    }
  ],
  "annotated_image": "data:image/jpeg;base64,/9j/4AAQ..."
}
```

### WebSocket `/ws/live`

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/live");

ws.onopen = () => {
  // Send compressed JPEG frame
  canvas.toBlob(blob => ws.send(blob), "image/jpeg", 0.5);
};

ws.onmessage = e => {
  const { detections, inference_time_ms } = JSON.parse(e.data);
  // Draw detections over local canvas — 60+ FPS local rendering
  detections.forEach(d => console.log(d.label, d.confidence, d.box));
};
```

### Python client

```python
import requests

with open("image.jpg", "rb") as f:
    res = requests.post("http://localhost:8000/predict",
                        files={"file": ("image.jpg", f, "image/jpeg")})

for d in res.json()["detections"]:
    print(f"{d['label']}  {d['confidence']*100:.1f}%  {d['box']}")
```

---

## 📊 Benchmarks

Measured on Intel Core i7 CPU (no GPU):

| Metric | Value | Notes |
|---|---|---|
| Model size | ~6.2 MB | `yolov8n.pt` |
| REST inference | 15 – 45 ms | CPU, 640px input |
| Live FPS (visual) | 60+ FPS | Local canvas rendering |
| Live FPS (inference) | 20 – 30 FPS | WebSocket round-trip |
| RAM usage | ~180 MB | FastAPI + Torch runtime |
| Cold start | < 2.5 s | Model cached after first load |

---

## 🧪 Testing

```bash
pytest -v
```

```
tests/test_health.py::test_health_check                          PASSED
tests/test_health.py::test_model_info                            PASSED
tests/test_model.py::test_preprocessing                          PASSED
tests/test_model.py::test_object_detector_inference              PASSED
tests/test_model.py::test_object_detector_frame_detection        PASSED
tests/test_validation.py::test_predict_invalid_content_type      PASSED
tests/test_validation.py::test_predict_empty_file                PASSED
tests/test_validation.py::test_predict_oversized_file            PASSED

======================= 8 passed ========================
```

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|---|---|---|
| `MODEL_NAME` | `yolov8n.pt` | YOLO weights file to load |
| `CONFIDENCE_THRESHOLD` | `0.5` | Minimum detection confidence (0–1) |
| `MAX_FILE_SIZE_MB` | `15` | Max upload size in MB |
| `DEVICE` | `auto` | `cpu` or `cuda` |

---

## 📄 License

Distributed under the [MIT License](LICENSE).
