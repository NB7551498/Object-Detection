# Architecture Decision Records (ADR) — VisionAI

This document records the key architectural and design decisions made in VisionAI, along with the context, alternatives considered, and justifications.

---

## ADR-001: Adoption of Ultralytics YOLOv8 for Object Detection

### Context
We needed an object detection engine that delivers production-grade bounding box accuracy while running smoothly on standard laptop CPUs without requiring dedicated CUDA GPUs.

### Decision
Adopt **Ultralytics YOLOv8** (`yolov8n.pt`).

### Consequences & Rationale
- **High Performance**: YOLOv8 Nano requires only ~3.2M parameters and achieves 15–45ms inference on standard x86 CPUs.
- **Pre-trained Coverage**: Includes 80 standard COCO classes out of the box.
- **Extensible**: Seamlessly supports custom fine-tuning and export to ONNX or OpenVINO.

---

## ADR-002: Decoupled Live WebSocket Rendering Architecture

### Context
Initial live streaming implementations encoded the entire annotated video frame as Base64 JPEG on the server and sent it back to the client. This saturated network bandwidth and capped rendering at 10–15 FPS with noticeable lag and flickering.

### Decision
Decouple camera display from model inference:
1. The browser displays the local webcam stream natively inside HTML5 `<video>` / `<canvas>` at full hardware 60 FPS.
2. Compressed frame snapshots are streamed over `/ws/live`.
3. The server returns only bounding box coordinates and latency metadata.
4. The client paints the bounding box overlay on top of the live feed.

### Consequences & Rationale
- Eliminates video stuttering and latency rubber-banding.
- Reduces network payload size by over 95% (from ~80 KB per frame to < 1 KB of JSON coordinates).
- Delivers a smooth, professional 60 FPS user experience even on slow connections.

---

## ADR-003: Vanilla JS Single-Page Application (SPA) vs. Heavy Frontend Frameworks

### Context
We evaluated whether to introduce Next.js, React, or Vue with npm build pipelines versus maintaining lightweight Vanilla JavaScript.

### Decision
Implement the entire VisionAI frontend using modern Vanilla ES6+, CSS variables, and HTML5 templates served directly by FastAPI.

### Consequences & Rationale
- **Zero Build Overhead**: Eliminates `node_modules`, webpack/vite bundlers, and compilation steps.
- **Fast Startup**: Instant cold boot (< 2.5 seconds) and tiny memory footprint.
- **Easy Deployment**: Single command (`uvicorn app.main:app`) runs both the API and the complete UI.
- **Maintainability**: Clear, readable code that doesn't suffer from dependency deprecation.

---

## ADR-004: Client-Side LocalStorage for Detection History and Analytics

### Context
We needed to display detection history and analytics across user sessions without introducing heavy external databases (PostgreSQL, Redis, Supabase) for local development.

### Decision
Store session detection logs, aggregated run counts, and class occurrences directly in browser `localStorage`.

### Consequences & Rationale
- Zero database configuration required for end users.
- Privacy-first: User images and detection records remain entirely on their own machine.
- Fast, synchronous reads and writes that instantly update the Dashboard and Analytics charts.

---

## ADR-005: Standalone PyTorch Training Pipeline (`train.py`)

### Context
Users requested rigorous model training capabilities to fine-tune weights on custom datasets with state-of-the-art augmentations.

### Decision
Build a dedicated `train.py` CLI utility with Albumentations-style augmentation (mosaic, MixUp, copy-paste, HSV jitter), cosine learning rate scheduling, early stopping, automated evaluation (`model.val()`), and automated best-weight export to `trained_model.pt`.

### Consequences & Rationale
- Provides reproducible, rigorous model training without cluttering the web API runtime.
- Works out of the box with built-in datasets (`coco128`) and custom YAML configurations.

---

## ADR-006: Defense-in-Depth Security & Hardening Architecture

### Context
Web-based AI inference services face distinct threat vectors including compute starvation DoS attacks, file upload tampering (MIME-spoofing, polyglot payloads, decompression bombs), Clickjacking, XSS, and WebSocket socket exhaustion.

### Decision
Implement an in-depth security subsystem in `app/security.py` featuring:
1. HTTP Security Headers (CSP, HSTS, X-Frame-Options: DENY, X-Content-Type-Options: nosniff, Permissions-Policy).
2. Thread-safe in-memory Sliding Window Rate Limiter.
3. Binary magic byte signature inspection for all uploads.
4. WebSocket connection capping and frame throttling.
5. Decompression bomb pixel thresholds and dimension bounds.
6. Sanitized exception handler preventing filesystem traceback leaks.

### Consequences & Rationale
- Protects the application against both web exploits and ML-specific compute starvation without requiring external enterprise WAF hardware.
- Native Python implementation runs zero external daemon dependencies (no Redis or external rate limiter needed for local deployments).
- Validated with automated unit and regression tests in `tests/test_security.py`.

