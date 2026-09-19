# Security Policy & Guidelines — VisionAI

This document outlines the security architecture, input validation rules, and vulnerability mitigation strategies for VisionAI.

---

## 1. Input Validation & File Upload Security

### MIME Type Enforcement
Files uploaded to `POST /predict` are strictly validated against an explicit whitelist:
```python
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp"}
```
Any file carrying a non-whitelisted MIME type is immediately rejected with `HTTP 400 Bad Request`.

### Payload Size Limits
To prevent buffer overflow and memory exhaustion attacks:
- Maximum upload size is strictly capped by `MAX_FILE_SIZE_BYTES` (default: 15 MB).
- File length is verified before passing bytes to PIL decoding or PyTorch tensor allocation:
```python
if len(image_bytes) > MAX_FILE_SIZE_BYTES:
    raise HTTPException(status_code=413, detail="File too large")
```
- Empty payloads (0 bytes) are rejected with `HTTP 400`.

### Image Decompression Bomb Protection
Pillow's internal safeguards prevent pixel decompression bombs. Images with corrupted headers or invalid byte streams trigger a handled exception and return a clean HTTP 400 response.

---

## 2. WebSocket Security & Streaming Safeguards

### Resource Exhaustion Prevention
- Live streaming frames on `/ws/live` are passed as compressed JPEG blobs (`quality: 0.5`).
- The backend does not buffer indefinite history in server memory; frames are evaluated statelessly and discarded immediately after inference.

### Safe Disconnect Handling
The WebSocket loop wraps all network operations in try/except blocks to gracefully catch `WebSocketDisconnect` without generating orphaned threads or hanging sockets.

---

## 3. Secrets & Configuration Management

### Zero Secrets in Source
- No API keys, passwords, or sensitive paths are stored in the codebase.
- Configuration is loaded exclusively via environment variables (`app/config.py`).
- `.env` and other secret stores are explicitly ignored in `.gitignore`.
- `.env.example` provides the safe public contract template.

---

## 4. Client-Side Security

### XSS Prevention
- All user-supplied filenames and labels rendered in the DOM are sanitized or populated using native `textContent` assignments rather than unsanitized `innerHTML`.
- SVG icons are hardcoded static assets without embedded script elements.

### Storage Isolation
- Session history and analytics are isolated to browser `localStorage` and never transmitted to external third-party tracking services.

---

## 5. Deployment Hardening Checklist

Before public exposure:
- [ ] Run behind a reverse proxy (e.g. Nginx, Caddy, or Cloudflare) with HTTPS/TLS termination.
- [ ] Implement rate limiting (e.g. 60 requests/minute per IP) on `POST /predict`.
- [ ] Configure restrictive CORS policies in FastAPI (`CORSMiddleware`) if frontend is hosted on a separate domain.
- [ ] Set `RELOAD=false` and run non-root Docker containers.
