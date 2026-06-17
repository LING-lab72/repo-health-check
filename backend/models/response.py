"""Unified API response models."""
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""

    code: int = Field(default=0, description="Status code. 0 = success, non-zero = error.")
    message: str = Field(default="success", description="Human-readable message.")
    data: T | None = Field(default=None, description="Response payload.")


class ErrorResponse(ApiResponse[None]):
    """Error response with no data payload."""

    code: int
    message: str
    data: None = None
