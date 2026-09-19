"""Security test suite verifying defense-in-depth security layers."""

import io
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.security import sanitize_filename, validate_image_magic_bytes

client = TestClient(app)


def test_security_headers_present():
    """Verify that hardened HTTP security headers are present on all responses."""
    response = client.get("/health")
    assert response.status_code == 200

    # Anti-clickjacking
    assert response.headers.get("x-frame-options") == "DENY"

    # Anti-MIME sniffing
    assert response.headers.get("x-content-type-options") == "nosniff"

    # XSS Protection
    assert response.headers.get("x-xss-protection") == "1; mode=block"

    # Content Security Policy (CSP)
    csp = response.headers.get("content-security-policy", "")
    assert "default-src 'self'" in csp
    assert "frame-ancestors 'none'" in csp

    # Permissions-Policy
    assert "camera=(self)" in response.headers.get("permissions-policy", "")


def test_magic_byte_validation():
    """Verify that magic byte validation catches spoofed image content types."""
    # Fake JPEG containing ASCII text
    fake_jpeg = b"This is a malicious shell script pretending to be a JPEG image."
    assert validate_image_magic_bytes(fake_jpeg, "image/jpeg") is False

    # Genuine JPEG
    img = Image.new("RGB", (20, 20), color="green")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    assert validate_image_magic_bytes(buf.getvalue(), "image/jpeg") is True


def test_reject_spoofed_mime_type_upload():
    """Verify API returns 400 when an uploaded file's binary content does not match its declared image MIME type."""
    fake_file_bytes = b"#!/bin/bash\necho 'Hacked'\n"
    response = client.post(
        "/predict",
        files={"file": ("malicious.jpg", fake_file_bytes, "image/jpeg")},
    )
    assert response.status_code == 400
    assert "binary signature" in response.json()["detail"].lower()


def test_filename_sanitization():
    """Verify that path traversal attempts in filenames are stripped cleanly."""
    assert sanitize_filename("../../etc/passwd") == "passwd"
    assert sanitize_filename("..\\..\\windows\\system32\\cmd.exe") == "cmd.exe"
    assert sanitize_filename("test;rm -rf;.png") == "testrm-rf.png"
    assert sanitize_filename("") == "upload.jpg"

