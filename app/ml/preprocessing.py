"""Preprocessing logic for converting images for YOLO inference."""

import io
from PIL import Image
from torchvision.transforms import functional as F


def preprocess_image(image_bytes: bytes, device: str = "cpu"):
    """Convert raw image bytes into a Pillow Image and a device-mapped tensor.

    Args:
        image_bytes: Raw bytes of the uploaded image file or video frame.
        device: The target compute device (e.g. 'cpu', 'cuda').

    Returns:
        A tuple of (PIL.Image, torch.Tensor).

    Raises:
        ValueError: If the image cannot be decoded.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as exc:
        raise ValueError(f"Unable to decode image bytes: {exc}")

    tensor = F.to_tensor(image).to(device)
    return image, tensor
