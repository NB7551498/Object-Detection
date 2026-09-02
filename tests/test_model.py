import io
from PIL import Image

from app.ml.inference import ObjectDetector
from app.ml.preprocessing import preprocess_image


def test_preprocessing():
    """Verify that preprocessing correctly parses image bytes into PIL and tensor."""
    # Create dummy image in memory
    img = Image.new("RGB", (150, 150), color="blue")
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    image_bytes = buffered.getvalue()

    # Preprocess
    pil_img, tensor = preprocess_image(image_bytes, device="cpu")
    
    assert pil_img.size == (150, 150)
    assert tensor.shape == (3, 150, 150)  # Shape should be (C, H, W)
    assert tensor.max() <= 1.0            # Normalized to [0, 1]
    assert tensor.min() >= 0.0


def test_object_detector_inference():
    """Verify that the ObjectDetector performs inference and returns valid keys."""
    # Create a simple red JPEG image in memory
    img = Image.new("RGB", (100, 100), color="red")
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    image_bytes = buffered.getvalue()

    # Initialize detector and run detection
    detector = ObjectDetector(confidence_threshold=0.5, device="cpu")
    detections, annotated_image_b64 = detector.detect(image_bytes)

    # Check results
    assert isinstance(detections, list)
    assert isinstance(annotated_image_b64, str)
    assert annotated_image_b64.startswith("data:image/jpeg;base64,")

    # If any objects are detected, verify keys
    for det in detections:
        assert "label" in det
        assert "confidence" in det
        assert "box" in det
        box = det["box"]
        assert "xmin" in box
        assert "ymin" in box
        assert "xmax" in box
        assert "ymax" in box


def test_object_detector_frame_detection():
    """Verify that detect_frame returns latency and detections for live streaming."""
    img = Image.new("RGB", (100, 100), color="green")
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    image_bytes = buffered.getvalue()

    detector = ObjectDetector(confidence_threshold=0.5, device="cpu")
    result = detector.detect_frame(image_bytes)

    assert "detections" in result
    assert "annotated_image" in result
    assert "inference_time_ms" in result
    assert isinstance(result["inference_time_ms"], float)
