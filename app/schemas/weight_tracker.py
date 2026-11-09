"""Pydantic schemas for weight tracking API"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class WeightEntryCreate(BaseModel):
    """Request model for creating a weight entry"""
    date: datetime = Field(..., description="Date of weight measurement")
    weight: float = Field(..., gt=0, description="Weight value (must be positive)")
    unit: str = Field(..., description="Unit: 'kg' or 'lb'")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes")

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2026-11-09T10:00:00Z",
                "weight": 10.5,
                "unit": "lb",
                "notes": "After morning meal"
            }
        }


class WeightEntryUpdate(BaseModel):
    """Request model for updating a weight entry"""
    date: Optional[datetime] = Field(None, description="Date of weight measurement")
    weight: Optional[float] = Field(None, gt=0, description="Weight value (must be positive)")
    unit: Optional[str] = Field(None, description="Unit: 'kg' or 'lb'")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes")


class WeightEntryResponse(BaseModel):
    """Response model for weight entry"""
    id: int
    date: datetime
    weight_kg: float
    weight_lb: float
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WeightEntryList(BaseModel):
    """Response model for list of weight entries"""
    entries: list[WeightEntryResponse]
    total: int
