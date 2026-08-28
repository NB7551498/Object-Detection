"""Preprocessing logic for converting images to PyTorch tensors."""

import io
from PIL import Image
from torchvision.transforms import functional as F
import torch


def preprocess_image(image_bytes: bytes, device: str = "cpu"):
    """Convert raw image bytes into a Pillow Image and a device-mapped tensor.

    Args:
        image_bytes: Raw bytes of the uploaded image file.
        device: The target compute device (e.g. 'cpu', 'cuda').

    Returns:
        A tuple of (PIL.Image, torch.Tensor). The tensor has shape (3, H, W)
        mapped to the specified device.

    Raises:
        ValueError: If the image cannot be decoded.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as exc:
        raise ValueError(f"Unable to decode image bytes: {exc}")

    # Convert to PyTorch Tensor: (H, W, C) -> (C, H, W) in range [0, 1]
    tensor = F.to_tensor(image).to(device)

    return image, tensor
