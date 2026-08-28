"""Pydantic schemas for API request validation and response serialization."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response schema for the health-check endpoint."""

    status: str = Field(..., example="ok", description="API health status")


class ModelInfoResponse(BaseModel):
    """Response schema for the active model configuration details."""

    model: str = Field(..., example="Faster R-CNN ResNet-50 FPN v2", description="Name of the model")
    device: str = Field(..., example="cpu", description="Compute device being used for inference")
    confidence_threshold: float = Field(..., example=0.5, description="Active minimum detection confidence")
    max_file_size_mb: int = Field(..., example=15, description="Maximum allowed file upload size in MB")


class BoundingBox(BaseModel):
    """Coordinates of a detected object's bounding box."""

    xmin: float = Field(..., description="Minimum X coordinate (left)")
    ymin: float = Field(..., description="Minimum Y coordinate (top)")
    xmax: float = Field(..., description="Maximum X coordinate (right)")
    ymax: float = Field(..., description="Maximum Y coordinate (bottom)")


class DetectionItem(BaseModel):
    """A single detected object with its class, confidence, and box."""

    label: str = Field(..., example="apple", description="Class name of the detected object")
    confidence: float = Field(..., example=0.9123, description="Model prediction score (0.0 to 1.0)")
    box: BoundingBox = Field(..., description="Bounding box coordinates in pixels")


class DetectionResponse(BaseModel):
    """Response schema for the object detection endpoint."""

    detections: list[DetectionItem] = Field(..., description="List of all detected objects")
    annotated_image: str = Field(
        ...,
        example="data:image/jpeg;base64,...",
        description="Base64-encoded JPEG image with bounding boxes drawn on it",
    )
