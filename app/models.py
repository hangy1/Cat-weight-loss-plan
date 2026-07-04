"""Pydantic models for request/response validation"""
from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from datetime import datetime


class CatRequest(BaseModel):
    """Request model for calorie calculation"""
    weight_kg: float = Field(..., gt=0, description="Cat's current weight in kilograms")
    life_stage: str = Field(..., description="Life stage: neutered_adult, intact_adult, inactive_obese_prone, kitten_growth")
    activity: str = Field(default="typical", description="Activity level: sedentary, typical, active, outdoor")
    bcs: int = Field(default=5, ge=1, le=9, description="Body Condition Score (1-9, where 5 is ideal)")

    class Config:
        json_schema_extra = {
            "example": {
                "weight_kg": 4.5,
                "life_stage": "neutered_adult",
                "activity": "typical",
                "bcs": 6
            }
        }


class WeightConversionRequest(BaseModel):
    """Request model for weight conversion"""
    weight: float = Field(..., gt=0, description="Weight value to convert")
    from_unit: str = Field(..., description="Source unit: 'kg' or 'lb'")

    class Config:
        json_schema_extra = {
            "example": {
                "weight": 10.0,
                "from_unit": "lb"
            }
        }


class WeightConversionResponse(BaseModel):
    """Response model for weight conversion"""
    weight_kg: float = Field(..., description="Weight in kilograms")
    weight_lb: float = Field(..., description="Weight in pounds")
    from_unit: str = Field(..., description="Original unit")


class CalorieResponse(BaseModel):
    """Response model for calorie calculation"""
    current_weight_kg: float = Field(..., description="Cat's current weight in kilograms")
    ideal_weight_kg: float = Field(..., description="Cat's ideal weight based on BCS")
    bcs: int = Field(..., description="Body Condition Score (1-9)")
    rer: int = Field(..., description="Resting Energy Requirement (based on ideal weight)")
    life_stage_factor: float = Field(..., description="Life stage multiplication factor")
    activity_factor: float = Field(..., description="Activity adjustment factor")
    calories: Dict[str, int] = Field(..., description="Min and recommended daily calories (MER)")

    class Config:
        json_schema_extra = {
            "example": {
                "current_weight_kg": 5.0,
                "ideal_weight_kg": 4.5,
                "bcs": 6,
                "rer": 197,
                "life_stage_factor": 1.3,
                "activity_factor": 1.0,
                "calories": {
                    "min": 237,
                    "recommended": 256
                }
            }
        }
