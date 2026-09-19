"""Preprocessing logic for converting images for YOLO inference."""

import io
from PIL import Image
from torchvision.transforms import functional as F

from app.config import MAX_IMAGE_DIMENSION

# Limit maximum decompression pixels to prevent decompression bomb attacks (~50 Megapixels)
Image.MAX_IMAGE_PIXELS = 50_000_000


def preprocess_image(image_bytes: bytes, device: str = "cpu"):
    """Convert raw image bytes into a Pillow Image and a device-mapped tensor.

    Args:
        image_bytes: Raw bytes of the uploaded image file or video frame.
        device: The target compute device (e.g. 'cpu', 'cuda').

    Returns:
        A tuple of (PIL.Image, torch.Tensor).

    Raises:
        ValueError: If the image cannot be decoded or exceeds dimension bounds.
    """
    try:
        # Verify and load image
        raw_image = Image.open(io.BytesIO(image_bytes))
        width, height = raw_image.size

        # Guard against dimension denial-of-service
        if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
            raise ValueError(
                f"Image dimensions ({width}x{height}) exceed maximum allowed {MAX_IMAGE_DIMENSION}px."
            )

        image = raw_image.convert("RGB")
    except Exception as exc:
        raise ValueError(f"Unable to decode image bytes: {exc}")

    tensor = F.to_tensor(image).to(device)
    return image, tensor

