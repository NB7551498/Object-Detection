"""Model loading module for YOLO object detection.

Loads the YOLOv8 model from ultralytics and maps it to the designated compute device.
"""

from ultralytics import YOLO


def load_model(model_name: str = "yolov8n.pt", device: str = "cpu") -> YOLO:
    """Load the YOLO object detection model.

    Args:
        model_name: Path or identifier of the YOLO weights (default 'yolov8n.pt').
        device: Target compute device ('cpu', 'cuda', etc.).

    Returns:
        The initialized YOLO model instance.
    """
    model = YOLO(model_name)
    return model
