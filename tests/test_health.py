from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Verify that the health check endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_model_info():
    """Verify that the model-info endpoint returns correct model metadata."""
    response = client.get("/model-info")
    assert response.status_code == 200
    data = response.json()
    assert "model" in data
    assert "device" in data
    assert "confidence_threshold" in data
    assert "max_file_size_mb" in data
    assert data["confidence_threshold"] == 0.5
