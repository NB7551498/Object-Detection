"""Image preprocessing for object detection.

Converts raw image bytes into a Pillow Image object and a normalized PyTorch tensor.
"""

import io
from PIL import Image
from torchvision.transforms import functional as F


def preprocess_image(image_bytes: bytes):
    """Convert raw image bytes into a Pillow Image and a model-ready tensor.

    Args:
        image_bytes: Raw bytes of the uploaded image file.

    Returns:
        A tuple of (PIL.Image, torch.Tensor). The tensor will have shape (3, H, W)
        and values in the range [0.0, 1.0].

    Raises:
        ValueError: If the image cannot be opened or converted.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as exc:
        raise ValueError(f"Could not open or convert the uploaded image: {exc}")

    # Convert to PyTorch Tensor: (H, W, C) -> (C, H, W) in range [0, 1]
    tensor = F.to_tensor(image)

    return image, tensor
