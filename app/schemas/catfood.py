"""
Pydantic schemas for cat food API
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class FoodSearchResult(BaseModel):
    """Cat food search result"""
    id: int
    name: str
    brand: Optional[str]
    type: Optional[str]  # 'wet' or 'dry'
    protein_pct: Optional[float]
    fat_pct: Optional[float]
    moisture_pct: Optional[float]
    kcal_per_kg: Optional[float]
    kcal_per_serving: Optional[float]
    serving_unit: Optional[str]


class FoodDetail(BaseModel):
    """Detailed cat food information"""
    id: int
    name: str
    brand: Optional[str]
    type: Optional[str]
    url: Optional[str]

    # As-fed nutrition
    protein_pct: Optional[float]
    fat_pct: Optional[float]
    fiber_pct: Optional[float]
    moisture_pct: Optional[float]
    ash_pct: Optional[float]
    taurine_pct: Optional[float]

    # Calorie info
    kcal_per_kg: Optional[float]
    kcal_per_serving: Optional[float]
    serving_unit: Optional[str]
    ga_basis: Optional[str]  # 'guaranteed' or 'typical'

    # Available sizes
    sizes: List[dict] = []


class DryMatterNutrition(BaseModel):
    """Dry matter nutrition (comparable across wet/dry)"""
    id: int
    name: str
    brand: Optional[str]
    type: Optional[str]
    moisture_pct: Optional[float]
    protein_dm: Optional[float]
    fat_dm: Optional[float]
    fiber_dm: Optional[float]
    kcal_per_kg: Optional[float]


class ServingCalculationRequest(BaseModel):
    """
    Request to calculate nutrition for a serving

    DRY FOOD: use 'grams' or 'cup'
    WET FOOD: use 'grams', 'oz' (weight, not fluid oz), or 'can'
    """
    product_id: int
    amount: float = Field(gt=0, description="Amount to feed")
    unit: str = Field(description="Dry: 'grams'/'cup' | Wet: 'grams'/'oz'/'can'")


class ServingCalculationResponse(BaseModel):
    """Nutrition calculation for a serving"""
    product_id: int
    product_name: str
    amount: float
    unit: str
    grams: float

    # Calculated nutrition
    calories: Optional[float]
    protein_g: Optional[float]
    fat_g: Optional[float]
    fiber_g: Optional[float]
    moisture_g: Optional[float]

    # As percentages (as-fed)
    protein_pct: Optional[float]
    fat_pct: Optional[float]
    fiber_pct: Optional[float]
    moisture_pct: Optional[float]
