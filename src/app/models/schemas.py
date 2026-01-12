"""Pydantic models for request/response validation."""

from enum import Enum

from pydantic import BaseModel


class ItemCreate(BaseModel):
    """Schema for creating a new item."""

    name: str
    description: str


class ItemResponse(BaseModel):
    """Schema for item response."""

    id: str
    name: str
    description: str


class Operation(str, Enum):
    """Supported calculator operations."""

    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"


class CalculateRequest(BaseModel):
    """Schema for calculate request."""

    a: int | float
    b: int | float
    operation: Operation


class CalculateResponse(BaseModel):
    """Schema for calculate response."""

    a: int | float
    b: int | float
    operation: str
    result: int | float
