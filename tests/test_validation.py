from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_predict_invalid_content_type():
    """Verify that uploading a non-image file type returns a 400 error."""
    files = {"file": ("test.txt", b"hello world", "text/plain")}
    response = client.post("/predict", files=files)
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_predict_empty_file():
    """Verify that uploading an empty file returns a 400 error."""
    files = {"file": ("empty.jpg", b"", "image/jpeg")}
    response = client.post("/predict", files=files)
    assert response.status_code == 400
    assert "Uploaded file is empty" in response.json()["detail"]


def test_predict_oversized_file():
    """Verify that uploading a file larger than MAX_FILE_SIZE returns a 413 error."""
    # Create a dummy payload of 16 MB (larger than 15 MB limit)
    large_payload = b"0" * (16 * 1024 * 1024)
    files = {"file": ("large.jpg", large_payload, "image/jpeg")}
    response = client.post("/predict", files=files)
    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]
