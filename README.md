# Object Detection API & Gemini-style Web UI

An interactive, containerized **Object Detection** service using a pre-trained **SSDLite MobileNet v3** model (trained on the COCO dataset with 80+ categories). It serves a sleek, responsive chat frontend styled like the **Gemini web client**.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start — Local](#quick-start--local)
- [Quick Start — Docker](#quick-start--docker)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## Overview

This project wraps an object detection model in a **FastAPI** web service. Features include:

- **SSDLite MobileNet v3** object detector running efficiently on CPU.
- Real-time image annotation (bounding boxes, class labels, and confidence percentages).
- **Gemini-style Chat UI** frontend to drag-and-drop or select images and see real-time object detection visual feeds side-by-side with tabular metadata.
- Automated API endpoints for external integrations.

---

## Project Structure

```
model-deployment/
├── app/
│   ├── __init__.py           # Package marker
│   ├── main.py               # FastAPI app, HTML routes, endpoints
│   ├── model.py              # Model loading, COCO mapping, box annotation
│   ├── preprocessing.py      # Image loading and tensor transforms
│   ├── schemas.py            # Pydantic schemas for object detection
│   └── templates/
│       └── index.html        # Gemini-style HTML/CSS/JS frontend
├── Dockerfile                # Container build file
├── .dockerignore             # Build context exclusions
├── requirements.txt          # Python dependencies
└── README.md                 # This file
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

Open **[http://localhost:8000/](http://localhost:8000/)** to interact with the web frontend.

---

## API Endpoints

### `GET /`

Returns the responsive HTML frontend client.

### `GET /health`

Returns `{"status": "ok"}` for basic uptime monitoring.

### `POST /predict`

Accepts an image upload and returns object coordinates + a base64-encoded annotated JPEG visualization.

**Request**: `multipart/form-data` with a `file` field.

**Accepted formats**: JPEG, PNG, WebP, BMP  
**Max file size**: 15 MB

**Example Response**:
```json
{
  "detections": [
    {
      "label": "apple",
      "confidence": 0.9414,
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

| Environment Variable | Default | Description |
| -------------------- | ------- | ----------- |
| `PORT`               | `8000`  | Port to bind the server on |

---

## License

This project is part of the **internSpark** internship program — Task 3 of 4.
