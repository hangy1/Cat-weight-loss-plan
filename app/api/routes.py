"""API route handlers"""
from fastapi import APIRouter, HTTPException
from app.models import (
    CatRequest,
    WeightConversionRequest,
    WeightConversionResponse,
    CalorieResponse
)
from app.services.calculator import calculate_calories, convert_weight
from app.core.config import settings

router = APIRouter()


@router.get("/")
def root():
    """API information and available endpoints"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": settings.DESCRIPTION,
        "endpoints": {
            "POST /calculate": "Calculate calorie requirements",
            "POST /convert-weight": "Convert weight between kg and lb",
            "GET /life-stages": "Get available life stages",
            "GET /activity-levels": "Get available activity levels",
            "GET /bcs-scores": "Get Body Condition Score (BCS) information",
            "GET /config": "Get full configuration",
            "GET /health": "Health check",
            "GET /docs": "Interactive API documentation"
        }
    }


@router.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": settings.PROJECT_NAME}


@router.get("/life-stages")
def get_life_stages():
    """Get all available life stages with their factor ranges"""
    life_stages = settings.life_stage_factors
    return {
        "life_stages": [
            {
                "id": key,
                "name": key.replace("_", " ").title(),
                "factors": {
                    "min": value["min"],
                    "recommended": value["recommended"],
                    "max": value["max"]
                },
                "description": value["description"]
            }
            for key, value in life_stages.items()
        ]
    }


@router.get("/activity-levels")
def get_activity_levels():
    """Get all available activity levels with their adjustment factors"""
    activity_levels = settings.activity_adjustment
    return {
        "activity_levels": [
            {
                "id": key,
                "name": key.replace("_", " ").title(),
                "factor": value["factor"],
                "description": value["description"]
            }
            for key, value in activity_levels.items()
        ]
    }


@router.get("/bcs-scores")
def get_bcs_scores():
    """Get Body Condition Score (BCS) information with weight adjustments"""
    bcs_data = settings.config_data["bcs_adjustment"]
    return {
        "bcs_scores": [
            {
                "score": int(key),
                "adjustment": value["adjustment"],
                "description": value["description"]
            }
            for key, value in bcs_data.items()
        ],
        "info": {
            "scale": "1-9, where 5 is ideal body condition",
            "formula": "ideal_weight = current_weight / (1 + adjustment)"
        }
    }


@router.get("/config")
def get_config():
    """Get the full configuration including all factors and constants"""
    return {
        "config": settings.config_data,
        "description": {
            "rer_multiplier": "Resting Energy Requirement multiplier (RER = k * weight^0.75)",
            "life_stage_factors": "Standard veterinary factors for different life stages",
            "activity_adjustment": "Optional activity level adjustments",
            "bcs_adjustment": "Body Condition Score adjustments for ideal weight calculation",
            "formula": "MER = RER(ideal_weight) × life_stage_factor × activity_factor"
        }
    }


@router.post("/convert-weight", response_model=WeightConversionResponse)
def convert_weight_endpoint(data: WeightConversionRequest):
    """
    Convert weight between kilograms and pounds

    Parameters:
    - weight: The weight value to convert
    - from_unit: The source unit ("kg" or "lb")

    Returns:
    - weight_kg: Weight in kilograms
    - weight_lb: Weight in pounds
    - from_unit: Original unit
    """
    if data.from_unit.lower() not in ["kg", "lb"]:
        raise HTTPException(
            status_code=400,
            detail="from_unit must be either 'kg' or 'lb'"
        )

    if data.weight <= 0:
        raise HTTPException(
            status_code=400,
            detail="Weight must be greater than 0"
        )

    return convert_weight(data.weight, data.from_unit)


@router.post("/calculate", response_model=CalorieResponse)
def calculate_endpoint(data: CatRequest):
    """
    Calculate daily calorie requirements for a cat using standard veterinary formula

    Parameters:
    - weight_kg: Cat's current weight in kilograms
    - life_stage: Life stage (neutered_adult, intact_adult, inactive_obese_prone, kitten_growth)
    - activity: Activity level (sedentary, typical, active, outdoor) - optional, defaults to typical
    - bcs: Body Condition Score (1-9, where 5 is ideal) - optional, defaults to 5

    Formula:
    - RER = 70 × (ideal_weight^0.75)
    - ideal_weight = current_weight / (1 + bcs_adjustment)
    - MER = RER × life_stage_factor × activity_factor
    - Safety floor: min calories >= 0.7 × RER(current_weight)

    Returns:
    - current_weight_kg: Cat's current weight
    - ideal_weight_kg: Calculated ideal weight based on BCS
    - bcs: Body Condition Score used
    - rer: Resting Energy Requirement (based on ideal weight)
    - life_stage_factor: Life stage multiplication factor
    - activity_factor: Activity adjustment factor
    - calories: Min (safety floor) and recommended daily calorie intake (MER)
    """
    try:
        return calculate_calories(
            weight_kg=data.weight_kg,
            life_stage=data.life_stage,
            activity=data.activity,
            bcs=data.bcs
        )
    except KeyError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid parameter: {str(e)}. Use the options endpoints to see valid choices."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
