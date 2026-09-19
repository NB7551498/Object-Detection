# Security Architecture & Hardening — VisionAI

This document outlines the multi-layered defense-in-depth security architecture implemented across VisionAI to prevent hacking, data tampering, denial of service, and resource exhaustion attacks.

---

## 1. Security Architecture Summary

```
                       INCOMING REQUEST / WEBSOCKET
                                    │
                                    ▼
         ┌─────────────────────────────────────────────────────┐
         │ 1. RateLimiterMiddleware (Sliding Window Per IP)   │ ──> HTTP 429 if flooded
         └──────────────────────────┬──────────────────────────┘
                                    │
                                    ▼
         ┌─────────────────────────────────────────────────────┐
         │ 2. SecurityHeadersMiddleware                        │ ──> Injects CSP, HSTS,
         │    (Anti-Clickjacking, Anti-MIME Sniff, CSP)        │     X-Frame-Options: DENY
         └──────────────────────────┬──────────────────────────┘
                                    │
                                    ▼
         ┌─────────────────────────────────────────────────────┐
         │ 3. CORSMiddleware (Configurable Origin Whitelist)   │ ──> Blocks unauthorized
         └──────────────────────────┬──────────────────────────┘     cross-site origins
                                    │
                                    ▼
         ┌─────────────────────────────────────────────────────┐
         │ 4. Optional API Key Verification (X-API-Key)        │ ──> HTTP 401 if invalid
         └──────────────────────────┬──────────────────────────┘
                                    │
                                    ▼
         ┌─────────────────────────────────────────────────────┐
         │ 5. Input Validation & Magic Byte Signature Check    │ ──> HTTP 400/413 if bad
         │    (MIME Whitelist, Magic Bytes, Max 15 MB)         │     format or spoofed
         └──────────────────────────┬──────────────────────────┘
                                    │
                                    ▼
         ┌─────────────────────────────────────────────────────┐
         │ 6. Dimension & Decompression Bomb Safeguard         │ ──> HTTP 400 if pixels
         │    (Max 8192px dimension, Max 50M pixels)           │     exceed limits
         └──────────────────────────┬──────────────────────────┘
                                    │
                                    ▼
         ┌─────────────────────────────────────────────────────┐
         │ 7. SafeExceptionMiddleware                          │ ──> Catches unhandled
         │    (Sanitized error JSON, zero trace leakage)       │     errors safely
         └─────────────────────────────────────────────────────┘
```

---

## 2. Implemented Defense Layers

### Layer 1: HTTP Security Headers
Applied automatically to every response via `SecurityHeadersMiddleware`:
- **`X-Frame-Options: DENY`**: Eliminates Clickjacking by prohibiting iframe embedding on third-party sites.
- **`X-Content-Type-Options: nosniff`**: Prevents browser MIME-confusion and script execution attacks.
- **`X-XSS-Protection: 1; mode=block`**: Activates reflective XSS filtering in legacy clients.
- **`Strict-Transport-Security (HSTS)`**: Enforces HTTPS connections (`max-age=31536000; includeSubDomains`).
- **`Content-Security-Policy (CSP)`**: Restricts script execution to safe internal origins and trusted font providers, completely disabling unauthorized external script injection.
- **`Permissions-Policy: camera=(self), microphone=(), geolocation=()`**: Locks down hardware camera access to VisionAI's exact origin, permanently disabling microphone and geolocation.

### Layer 2: Sliding-Window Rate Limiting (Anti-DoS)
Inference is compute-heavy. An attacker attempting to saturate CPU/GPU resources is throttled:
- Governed by `RateLimiterMiddleware` in `app/security.py`.
- Thread-safe sliding window tracking per client IP address.
- Configured by `RATE_LIMIT_PER_MINUTE` (default: 120 req/min).
- Requests exceeding the threshold receive `HTTP 429 Too Many Requests` with a dynamic `Retry-After` header.

### Layer 3: Binary Magic Byte Validation (Anti-MIME Spoofing)
- Attackers cannot rename a malicious executable, shell script, or HTML file to `exploit.jpg`.
- `validate_image_magic_bytes()` checks the actual binary byte header (`\xff\xd8\xff` for JPEG, `\x89PNG` for PNG, `RIFF...WEBP` for WebP, `BM` for BMP).
- Spoofed files are immediately rejected with `HTTP 400 Bad Request`.

### Layer 4: Filename Sanitization & Path Traversal Prevention
- `sanitize_filename()` strips directory separators (`/`, `\`), null bytes (`\x00`), and dangerous shell characters.
- Defends against directory climbing (e.g. `../../etc/passwd` or `..\system32\cmd.exe`).

### Layer 5: Decompression Bomb & Memory Exhaustion Defense
- Pillow's decompression bomb ceiling is enforced at `Image.MAX_IMAGE_PIXELS = 50_000_000`.
- Max dimension bounds check in `app/ml/preprocessing.py` blocks images with width or height > `MAX_IMAGE_DIMENSION` (8192px).
- Maximum upload byte length is enforced at `MAX_FILE_SIZE_BYTES` (15 MB) before decoding image bytes.

### Layer 6: WebSocket Security & Abuse Prevention
Implemented in `WebSocketSecurityManager`:
- **Connection Capping**: Enforces `MAX_WS_CONNECTIONS_PER_IP` (default: 5 concurrent sockets) to prevent file descriptor exhaustion.
- **Frame Rate Throttling**: Limits stream processing to ~30 FPS per socket, discarding microsecond frame floods.
- **Frame Size Caps**: Drops individual frames exceeding 5 MB to prevent memory bloat.
- **Safe Lifecycle**: Disconnections are caught and cleanly reclaimed without hanging sockets.

### Layer 7: Traceback Leakage & Information Disclosure Prevention
- `SafeExceptionMiddleware` intercepts any unhandled exception.
- Internal operating system file paths, stack traces, and library internals are never returned to the browser.
- Standardized sanitized error responses are returned (`HTTP 500: An internal server error occurred`).

### Layer 8: Optional API Key Protection
- Configure `API_KEY=your_secret_key` in `.env` to enforce authentication.
- REST endpoints automatically require the `X-API-Key` header when enabled.

---

## 3. Security Verification

Automated security regression tests are maintained in [`tests/test_security.py`](../tests/test_security.py):
```bash
pytest tests/test_security.py -v
```
- `test_security_headers_present`: Verifies CSP, HSTS, X-Frame-Options, X-Content-Type-Options.
- `test_magic_byte_validation`: Verifies binary header discrimination against spoofed payloads.
- `test_reject_spoofed_mime_type_upload`: Verifies `POST /predict` blocks fake images.
- `test_filename_sanitization`: Verifies path traversal neutralization.
