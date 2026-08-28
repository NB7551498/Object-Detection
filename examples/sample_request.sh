#!/usr/bin/env bash
# ── Example: Classify an image using the Model Deployment API ────────
#
# Prerequisites:
#   - The API server is running on http://localhost:8000
#   - You have a test image (e.g., test_image.jpg)
#
# Usage:
#   bash examples/sample_request.sh <path-to-image>

IMAGE_PATH="${1:-test_image.jpg}"

echo "=== Health Check ==="
curl -s http://localhost:8000/health | python -m json.tool
echo ""

echo "=== Prediction ==="
curl -s -X POST http://localhost:8000/predict \
  -F "file=@${IMAGE_PATH}" \
  | python -m json.tool
