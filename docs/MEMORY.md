# Project Memory — VisionAI

This document maintains the active context, runtime status, and operational state of VisionAI.

---

## 1. Current Status
- **Application State**: Fully operational.
- **Frontend**: VisionAI dark-first SPA (Dashboard, Detect, History, Analytics, Models, Settings) running at [http://localhost:8000](http://localhost:8000).
- **Backend**: FastAPI with async REST (`/predict`) and WebSocket (`/ws/live`) endpoints.
- **Model Engine**: Ultralytics YOLOv8 Nano (`yolov8n.pt`) with 80 COCO classes.
- **Training Pipeline**: `train.py` complete with cosine LR, Albumentations-style augmentation, early stopping, and `TRAINING.md` guide.
- **Documentation**: Complete Vibe Coding structure (`PRD.md`, `ARCHITECTURE.md`, `DESIGN.md`, `RULES.md`, `TASKS.md`, `DECISIONS.md`, `MEMORY.md`, `TEST_PLAN.md`, `SECURITY.md`, `.env.example`, `.cursor/rules/`).

---

## 2. Completed Milestones
- [x] Converted legacy chat UI into modern dark-first **VisionAI** product UI.
- [x] Fixed live camera idle canvas layout to ensure centered viewport status.
- [x] Decoupled webcam rendering to deliver 60+ FPS native visuals.
- [x] Built `train.py` with custom CLI args, dataset download, validation, and auto weight export.
- [x] Added `matplotlib`, `opencv-python`, `psutil`, `polars`, and `ultralytics-thop` to `requirements.txt`.
- [x] Authored comprehensive documentation suite matching the Beginner-to-Production Vibe Coding standard.
- [x] Implemented production security layer (CSP, HSTS, rate limiter, anti-spoof magic bytes, DoS safeguards).
- [x] Verified 100% pass rate across automated test suite (12 passed).

---

## 3. Current Task
- Production security layer operational and verified.


---

## 4. Known Issues & Mitigations
- **Issue**: On Windows terminal, running long training tasks in foreground locks the CLI.  
  **Mitigation**: Background tasks or detached processes with redirected log output (`runs/detect/...`).
- **Issue**: CPU-only systems take ~2–3 hours to train 50 epochs on COCO128.  
  **Mitigation**: Use GPU when available (`--device cuda`), or fine-tune with smaller epoch counts (`--epochs 15`).

---

## 5. Next Steps & Roadmap
- [ ] Add one-click sample image selector in the upload drop-zone for quick testing.
- [ ] Implement ONNX runtime export option for even faster edge CPU inference.
- [ ] Add live confidence threshold slider on the live camera viewport for real-time sensitivity tuning.
