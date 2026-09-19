# Test Plan & Verification Checklist — VisionAI

This document defines what "working" actually means for VisionAI across functionality, UI, streaming, and security.

---

## 1. Automated Testing (`pytest`)

Run the automated test suite locally:
```bash
pytest -v
```

### Automated Test Matrix
| Test File | Test Case | Expected Outcome | Status |
|---|---|---|---|
| `test_health.py` | `test_health_check` | Returns HTTP 200 and `{"status": "ok"}` | PASS |
| `test_health.py` | `test_model_info` | Returns HTTP 200 with model name and device info | PASS |
| `test_model.py` | `test_preprocessing` | Validates Pillow image normalization and tensor conversions | PASS |
| `test_model.py` | `test_object_detector_inference` | Runs model inference, returns detections and base64 image | PASS |
| `test_model.py` | `test_object_detector_frame_detection` | Fast inference on raw frame bytes returning latency and boxes | PASS |
| `test_security.py` | `test_security_headers_present` | Verifies CSP, HSTS, X-Frame-Options, X-Content-Type-Options | PASS |
| `test_security.py` | `test_magic_byte_validation` | Blocks fake/spoofed image binary payloads | PASS |
| `test_security.py` | `test_reject_spoofed_mime_type_upload` | Uploading script as JPEG returns HTTP 400 | PASS |
| `test_security.py` | `test_filename_sanitization` | Neutralizes path traversal attempts in filenames | PASS |
| `test_validation.py` | `test_predict_invalid_content_type` | Uploading a text or PDF file returns HTTP 400 error | PASS |
| `test_validation.py` | `test_predict_empty_file` | Uploading a 0-byte file returns HTTP 400 error | PASS |
| `test_validation.py` | `test_predict_oversized_file` | Uploading file > 15 MB returns HTTP 413 error | PASS |


---

## 2. Interactive Feature Verification Checklist

### Static Image Detection
- [ ] Drag-and-drop an image onto the drop zone: upload begins immediately.
- [ ] Multi-step progress indicator displays four status steps with active spinner.
- [ ] Annotated result renders with colored bounding boxes and confidence scores.
- [ ] Table lists detected objects, confidence percentage progress bars, and labels.
- [ ] "Download" button saves the annotated JPEG locally.
- [ ] "Run Again" resets the workspace back to the upload state.
- [ ] Detection is logged in LocalStorage and increments Dashboard counts.

### Live Camera Mode
- [ ] Click "Start Camera": browser requests camera permissions.
- [ ] Local video stream displays smoothly at 60 FPS.
- [ ] HUD displays red `LIVE` indicator, FPS count, inference latency (ms), and object count.
- [ ] "Stop Camera" closes webcam stream, clears canvas, and resets placeholder to centered state.
- [ ] Disconnecting network or reloading page handles WebSocket teardown cleanly without server crashes.

### Navigation & Views
- [ ] **Dashboard**: Displays Total Runs, Objects Found, Avg Confidence, and recent items.
- [ ] **Detect**: Toggles between Image Upload and Live Camera without tab reloads.
- [ ] **History**: Displays previous runs with timestamps and "Clear History" button.
- [ ] **Analytics**: Renders class distribution bars based on actual detection data.
- [ ] **Models**: Displays YOLOv8 active weights, device target, and 80 COCO classes.
- [ ] **Settings**: Lists backend parameters (model, device, threshold, max size).

---

## 3. Responsive & Device Testing

| Viewport | Target Device | Checklist |
|---|---|---|
| **1440px** | Desktop / Large Monitor | Fixed 228px sidebar, two-column results layout, full HUD. |
| **768px** | Tablet | Collapsed sidebar / drawer toggle, wrapped result cards. |
| **375px** | Mobile Smartphone | Hamburger menu, off-canvas drawer, stacked single-column layout. |

---

## 4. Edge Cases & Resilience
- [ ] Non-image files (e.g. `.exe`, `.pdf`) must be rejected with user-friendly error banners.
- [ ] Zero detections (e.g. plain white image) displays "No objects detected" empty table row instead of crash.
- [ ] Corrupt or truncated image files handle gracefully with HTTP 400.
- [ ] Rapid toggling of "Start Camera" / "Stop Camera" does not produce race conditions.
