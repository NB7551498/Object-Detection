"""Model loading, inference, and visualization logic for Object Detection.

Loads the pre-trained SSDLite MobileNet v3 model from torchvision and performs
inference, returning labels, bounding boxes, and base64-encoded annotated images.
"""

import base64
import io
import torch
from PIL import Image, ImageDraw, ImageFont
from torchvision.models.detection import fasterrcnn_resnet50_fpn_v2, FasterRCNN_ResNet50_FPN_V2_Weights

# Load COCO categories directly from weights metadata
_WEIGHTS = FasterRCNN_ResNet50_FPN_V2_Weights.DEFAULT
_COCO_CLASSES = _WEIGHTS.meta["categories"]


def load_model(model_path: str = None) -> torch.nn.Module:
    """Load the pre-trained Faster R-CNN ResNet50 FPN v2 model.

    Args:
        model_path: Ignored, as we load pre-trained COCO weights directly.

    Returns:
        The model in eval mode, mapped to CPU.
    """
    model = fasterrcnn_resnet50_fpn_v2(weights=_WEIGHTS)
    model.eval()
    return model


def predict(model: torch.nn.Module, image: Image.Image, tensor: torch.Tensor, confidence_threshold: float = 0.5):
    """Run object detection on the image and return bounding boxes and labels.

    Args:
        model: Loaded Faster R-CNN object detection model.
        image: Original PIL Image (needed for drawing annotations).
        tensor: Preprocessed tensor of shape (3, H, W).
        confidence_threshold: Min confidence score (0.0 to 1.0) to filter detections.

    Returns:
        A tuple of (detections_list, base64_annotated_image_string).
    """
    # Run model (expects a list of tensors)
    with torch.no_grad():
        predictions = model([tensor])
        
    pred = predictions[0]
    boxes = pred["boxes"].cpu()
    labels = pred["labels"].cpu()
    scores = pred["scores"].cpu()

    # Filter detections
    keep = scores >= confidence_threshold
    boxes = boxes[keep]
    labels = labels[keep]
    scores = scores[keep]

    detections = []
    annotated_image = image.copy()
    draw = ImageDraw.Draw(annotated_image)

    # Use default font or attempt to load basic font
    try:
        # Load default font
        font = ImageFont.load_default()
    except Exception:
        font = None

    # Colors for different classes (simple palette)
    colors = ["#FF3B30", "#34C759", "#007AFF", "#FF9500", "#AF52DE", "#5AC8FA"]

    for i in range(len(boxes)):
        box = boxes[i].tolist()  # [xmin, ymin, xmax, ymax]
        class_id = labels[i].item()
        score = scores[i].item()
        
        # SSDLite MobileNet category labels are 0-indexed corresponding to _COCO_CLASSES
        # Note: torchvision detection weights mapping matches the categories list indices
        if class_id < len(_COCO_CLASSES):
            label = _COCO_CLASSES[class_id]
        else:
            label = f"object_{class_id}"

        # Store detection info
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

        # Draw label text background
        text = f"{label} {score:.0%}"
        
        # Get text size
        if hasattr(draw, "textbbox") and font:
            text_box = draw.textbbox((box[0], box[1]), text, font=font)
            draw.rectangle([text_box[0], text_box[1] - 4, text_box[2] + 4, text_box[3] + 2], fill=color)
        else:
            # Simple text bounding box fallback
            draw.rectangle([box[0], box[1] - 15, box[0] + 80, box[1]], fill=color)

        # Draw text
        draw.text((box[0] + 2, box[1] - 13 if font else box[1] - 12), text, fill="white", font=font)

    # Convert annotated image to base64 string
    buffered = io.BytesIO()
    annotated_image.save(buffered, format="JPEG")
    base64_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    annotated_image_b64 = f"data:image/jpeg;base64,{base64_str}"

    return detections, annotated_image_b64
