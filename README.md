# Object Detection API & Gemini-style Web UI

An interactive, production-grade **Object Detection** service using a pre-trained **Faster R-CNN ResNet-50 FPN v2** model (COCO dataset, 80+ categories) with a sleek, responsive chat frontend styled like the **Gemini web client**.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Project Architecture](#project-architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start — Local](#quick-start--local)
- [Quick Start — Docker](#quick-start--docker)
- [Automated Testing](#automated-testing)
- [CI/CD Pipeline](#cicd-pipeline)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)

---

## Overview

This project wraps an advanced computer vision model in a **FastAPI** web service. Features include:

- **Faster R-CNN ResNet-50 FPN v2** object detector running efficiently on CPU/GPU.
- Real-time image annotation (bounding boxes, class labels, and confidence percentages).
- **Gemini-style Chat UI** frontend to drag-and-drop or select images and see real-time object detection visual feeds side-by-side with tabular metadata.
- Automated API endpoints for external integrations.
- Pydantic schema validation for request-response safety.
- Version-pinned dependencies and lockfile setup for maximum reproducibility.
- Full automated test suite using `pytest` and integrated GitHub Actions CI.

---

## Project Architecture

```
                 ┌───────────────┐
                 │    Web UI     │
                 └───────┬───────┘
                         │ (AJAX /predict)
                         ▼
                 ┌───────────────┐
                 │  FastAPI API  │
                 └───────┬───────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
    GET /health   GET /model-info  POST /predict
         │               │               │
      [Status]      [Metadata]     [ML Pipeline]
                                         │
                                         ▼
                                 ┌───────────────┐
                                 │Preprocess PIL │
                                 └───────┬───────┘
                                         │
                                         ▼
                                 ┌───────────────┐
                                 │ PyTorch Model │
                                 └───────┬───────┘
                                         │
                                         ▼
                                 ┌───────────────┐
                                 │  Postprocess  │
                                 └───────┬───────┘
                                         │ (Draw Box + Label)
                                         ▼
                                 ┌───────────────┐
                                 │ Base64 Image  │
                                 └───────────────┘
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
│   ├── main.py               # FastAPI entrypoint, lifespan configuration
│   ├── config.py             # Environment variable configuration loading
│   ├── schemas.py            # Pydantic schemas (Request/Response validation)
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py         # HTTP route definitions
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── model.py          # Faster R-CNN initialization onto CPU/GPU
│   │   ├── preprocessing.py  # Image-to-tensor conversions
│   │   └── inference.py      # ObjectDetector service runner & annotation logic
│   └── templates/
│       └── index.html        # Gemini-style HTML/CSS/JS frontend
├── tests/
│   ├── __init__.py           # Package marker
│   ├── test_health.py        # API health and model metadata tests
│   ├── test_validation.py    # Payload size and format validation tests
│   └── test_model.py         # Tensor shape and inference model tests
├── Dockerfile                # Pinned production container setup
├── .dockerignore             # Context exclusion rules
├── requirements.txt          # Python dependency versions
└── README.md                 # Project documentation
```

---

## Prerequisites

| Tool    | Version | Purpose                  |
| ------- | ------- | ------------------------ |
| Python  | 3.11+   | Runtime                  |
| pip     | latest  | Dependency management    |
| Docker  | 20.10+  | Containerization         |

---

## Quick Start — Local

### 1. Clone & enter the project

```bash
cd model-deployment
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
# Install CPU-only PyTorch (much smaller download ~200MB)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies
pip install -r requirements.txt
```

### 4. Start the server

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

- Open **[http://localhost:8000/](http://localhost:8000/)** in your browser to access the Gemini Chat UI.
- Open **[http://localhost:8000/docs](http://localhost:8000/)** to access the Swagger API docs.

---

## Quick Start — Docker

### 1. Build the image

```bash
docker build -t object-detection-app .
```

### 2. Run the container

```bash
docker run -p 8000:8000 object-detection-app
```

---

## Automated Testing

The project uses `pytest` and `httpx` for API testing. The tests verify endpoints, validation constraints, and the ML preprocessing shapes.

To run the test suite locally:

```bash
pytest
```

**Output**:
```
tests\test_health.py ..                                                  [ 28%]
tests\test_model.py ..                                                   [ 57%]
tests\test_validation.py ...                                             [100%]
======================= 7 passed in 21.71s ========================
```

---

## CI/CD Pipeline

A continuous integration workflow is set up via **GitHub Actions** (`.github/workflows/ci.yml`). 
On every `push` or `pull_request` to `main` and `learn` branches:
1. The codebase is checked out.
2. Python 3.11 is set up with caching enabled.
3. Dependencies are installed using the fast CPU-only PyTorch index.
4. The complete `pytest` test suite is executed.

---

## API Endpoints

### `GET /`
Serves the Gemini-style frontend.

### `GET /health`
Returns `{"status": "ok"}` for uptime verification.

### `GET /model-info`
Returns active configuration parameters.
```json
{
  "model": "fasterrcnn_resnet50_fpn_v2",
  "device": "cpu",
  "confidence_threshold": 0.5,
  "max_file_size_mb": 15
}
```

### `POST /predict`
Performs object detection on uploaded image.

**Request**: `multipart/form-data` with `file` field. (JPEG, PNG, WebP, BMP | Max: 15 MB)

**Response**:
```json
{
  "detections": [
    {
      "label": "apple",
      "confidence": 0.9993,
      "box": {
        "xmin": 36.4,
        "ymin": 76.5,
        "xmax": 352.1,
        "ymax": 420.3
      }
    }
  ],
  "annotated_image": "data:image/jpeg;base64,..."
}
```

---

## Configuration

The application configures itself using environment variables (with safe fallbacks):

| Environment Variable | Default | Description |
| -------------------- | ------- | ----------- |
| `CONFIDENCE_THRESHOLD`| `0.5` | Minimum score to keep detection |
| `MODEL_NAME`         | `fasterrcnn_resnet50_fpn_v2` | PyTorch torchvision model identifier |
| `MAX_FILE_SIZE_MB`   | `15` | Maximum upload size in Megabytes |
| `DEVICE`             | auto-detected | Compute target (`cpu` or `cuda`) |
