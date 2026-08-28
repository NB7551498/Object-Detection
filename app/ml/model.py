"""Model loading module for object detection.

Loads the pre-trained Faster R-CNN model weights and maps it to the
designated compute device.
"""

import torch
from torchvision.models.detection import (
    fasterrcnn_resnet50_fpn_v2,
    FasterRCNN_ResNet50_FPN_V2_Weights,
)

# Load COCO categories from weights metadata
_WEIGHTS = FasterRCNN_ResNet50_FPN_V2_Weights.DEFAULT
COCO_CLASSES = _WEIGHTS.meta["categories"]


def load_model(device: str = "cpu") -> torch.nn.Module:
    """Load the pre-trained Faster R-CNN ResNet50 FPN v2 model.

    Args:
        device: The target compute device (e.g. 'cpu', 'cuda').

    Returns:
        The loaded model placed on the specified device in evaluation mode.
    """
    model = fasterrcnn_resnet50_fpn_v2(weights=_WEIGHTS)
    model.to(device)
    model.eval()
    return model
