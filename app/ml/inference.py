"""Inference wrapper class using YOLOv8 for object detection and live streaming."""

import base64
import io
import time
from PIL import Image

from app.ml.model import load_model
from app.ml.preprocessing import preprocess_image


class ObjectDetector:
    """Service class encapsulating YOLO model loading, inference, and visualization."""

    def __init__(self, model_name: str = "yolov8n.pt", confidence_threshold: float = 0.5, device: str = "cpu"):
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self.device = device
        print(f"Initializing YOLO ObjectDetector ({self.model_name}) on device: {self.device}")
        self.model = load_model(model_name=self.model_name, device=self.device)

    def detect(self, image_bytes: bytes):
        """Run object detection on raw image bytes.

        Args:
            image_bytes: Raw upload image bytes.

        Returns:
            A tuple of (detections_list, base64_annotated_image_string).
        """
        pil_image, _ = preprocess_image(image_bytes, device=self.device)
        return self._detect_pil(pil_image)

    def _detect_pil(self, pil_image: Image.Image):
        # Run YOLO prediction
        results = self.model.predict(
            source=pil_image,
            conf=self.confidence_threshold,
            device=self.device,
            verbose=False
        )

        result = results[0]
        boxes = result.boxes
        names = result.names

        detections = []
        if boxes is not None and len(boxes) > 0:
            xyxy = boxes.xyxy.cpu().numpy()
            confs = boxes.conf.cpu().numpy()
            clss = boxes.cls.cpu().numpy().astype(int)

            for i in range(len(xyxy)):
                cls_id = clss[i]
                label = names.get(cls_id, f"object_{cls_id}")
                conf = float(confs[i])
                box_coords = xyxy[i].tolist()

                detections.append({
                    "label": label,
                    "confidence": round(conf, 4),
                    "box": {
                        "xmin": round(box_coords[0], 1),
                        "ymin": round(box_coords[1], 1),
                        "xmax": round(box_coords[2], 1),
                        "ymax": round(box_coords[3], 1)
                    }
                })

        # Generate annotated image
        # result.plot() returns a numpy array in BGR format
        annotated_bgr = result.plot()
        annotated_pil = Image.fromarray(annotated_bgr[..., ::-1])

        buffered = io.BytesIO()
        annotated_pil.save(buffered, format="JPEG", quality=85)
        base64_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        annotated_image_b64 = f"data:image/jpeg;base64,{base64_str}"

        return detections, annotated_image_b64

    def detect_frame(self, image_bytes: bytes):
        """Optimized detection for real-time video frames.

        Args:
            image_bytes: Raw JPEG/PNG frame bytes.

        Returns:
            A dict with detections, annotated_image base64, and latency in ms.
        """
        start_time = time.time()
        detections, annotated_image_b64 = self.detect(image_bytes)
        inference_time_ms = round((time.time() - start_time) * 1000, 1)

        return {
            "detections": detections,
            "annotated_image": annotated_image_b64,
            "inference_time_ms": inference_time_ms
        }
