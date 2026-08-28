"""Inference wrapper class separating model execution from API routes."""

import base64
import io
import torch
from PIL import Image, ImageDraw, ImageFont

from app.ml.model import load_model, COCO_CLASSES
from app.ml.preprocessing import preprocess_image


class ObjectDetector:
    """Service class encapsulating model loading, inference, and visualization."""

    def __init__(self, confidence_threshold: float = 0.5, device: str = "cpu"):
        self.confidence_threshold = confidence_threshold
        self.device = device
        print(f"Initializing ObjectDetector on device: {self.device}")
        self.model = load_model(device=self.device)

    def detect(self, image_bytes: bytes):
        """Run object detection on raw image bytes.

        Args:
            image_bytes: Raw upload image bytes.

        Returns:
            A tuple of (detections_list, base64_annotated_image_string).
        """
        # Preprocess
        pil_image, input_tensor = preprocess_image(image_bytes, device=self.device)

        # Run model (expects a list of tensors)
        with torch.no_grad():
            predictions = self.model([input_tensor])

        pred = predictions[0]
        boxes = pred["boxes"].cpu()
        labels = pred["labels"].cpu()
        scores = pred["scores"].cpu()

        # Filter by confidence threshold
        keep = scores >= self.confidence_threshold
        boxes = boxes[keep]
        labels = labels[keep]
        scores = scores[keep]

        detections = []
        annotated_image = pil_image.copy()
        draw = ImageDraw.Draw(annotated_image)

        try:
            font = ImageFont.load_default()
        except Exception:
            font = None

        colors = ["#FF3B30", "#34C759", "#007AFF", "#FF9500", "#AF52DE", "#5AC8FA"]

        for i in range(len(boxes)):
            box = boxes[i].tolist()  # [xmin, ymin, xmax, ymax]
            class_id = labels[i].item()
            score = scores[i].item()

            if class_id < len(COCO_CLASSES):
                label = COCO_CLASSES[class_id]
            else:
                label = f"object_{class_id}"

            detections.append({
                "label": label,
                "confidence": round(score, 4),
                "box": {
                    "xmin": round(box[0], 1),
                    "ymin": round(box[1], 1),
                    "xmax": round(box[2], 1),
                    "ymax": round(box[3], 1)
                }
            })

            # Draw bounding box
            color = colors[class_id % len(colors)]
            draw.rectangle(box, outline=color, width=3)

            # Draw label tag
            text = f"{label} {score:.0%}"
            if hasattr(draw, "textbbox") and font:
                text_box = draw.textbbox((box[0], box[1]), text, font=font)
                draw.rectangle([text_box[0], text_box[1] - 4, text_box[2] + 4, text_box[3] + 2], fill=color)
            else:
                draw.rectangle([box[0], box[1] - 15, box[0] + 80, box[1]], fill=color)

            draw.text((box[0] + 2, box[1] - 13 if font else box[1] - 12), text, fill="white", font=font)

        # Convert annotated image to base64 string
        buffered = io.BytesIO()
        annotated_image.save(buffered, format="JPEG")
        base64_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        annotated_image_b64 = f"data:image/jpeg;base64,{base64_str}"

        return detections, annotated_image_b64
