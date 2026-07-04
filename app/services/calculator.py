"""Calculator service for calorie and weight conversions"""
from app.core.config import settings


# Weight conversion constants
KG_TO_LB = 2.20462
LB_TO_KG = 0.453592


def kg_to_lb(weight_kg: float) -> float:
    """Convert weight from kilograms to pounds"""
    return weight_kg * KG_TO_LB


def lb_to_kg(weight_lb: float) -> float:
    """Convert weight from pounds to kilograms"""
    return weight_lb * LB_TO_KG


def calculate_rer(weight_kg: float) -> float:
    """Calculate Resting Energy Requirement (RER)"""
    k = settings.constants["rer_multiplier"]
    return k * (weight_kg ** 0.75)


def calculate_ideal_weight(current_weight_kg: float, bcs: int) -> float:
    """
    Calculate ideal weight based on Body Condition Score (BCS)

    Formula: ideal_weight = current_weight / (1 + adjustment)

    Args:
        current_weight_kg: Cat's current weight in kilograms
        bcs: Body Condition Score (1-9, where 5 is ideal)

    Returns:
        Ideal weight in kilograms
    """
    bcs_config = settings.config_data["bcs_adjustment"][str(bcs)]
    adjustment = bcs_config["adjustment"]

    ideal_weight = current_weight_kg / (1 + adjustment)
    return ideal_weight


def calculate_calories(weight_kg: float, life_stage: str, activity: str = "typical", bcs: int = 5) -> dict:
    """
    Calculate daily calorie requirements for a cat using standard veterinary formula

    Formula:
        - If BCS != 5: Calculate ideal weight, use it for RER
        - RER = 70 × (weight_kg^0.75)
        - MER = RER × life_stage_factor × activity_adjustment
        - Safety floor: minimum calories = 0.7 × RER (based on current weight)

    Args:
        weight_kg: Cat's current weight in kilograms
        life_stage: Life stage (neutered_adult, intact_adult, inactive_obese_prone, kitten_growth)
        activity: Activity level (sedentary, typical, active, outdoor) - defaults to typical
        bcs: Body Condition Score (1-9, where 5 is ideal) - defaults to 5

    Returns:
        Dictionary with current_weight, ideal_weight, rer, life_stage_factor, activity_factor,
        and calorie range (min/rec/max)
    """
    # Calculate ideal weight based on BCS
    ideal_weight = calculate_ideal_weight(weight_kg, bcs)

    # Use ideal weight for RER calculation to support weight goals
    rer = calculate_rer(ideal_weight)

    # Calculate current weight RER for safety floor
    current_rer = calculate_rer(weight_kg)

    # Get life stage factors
    life_stage_config = settings.life_stage_factors[life_stage]
    life_stage_min = life_stage_config["min"]
    life_stage_rec = life_stage_config["recommended"]
    life_stage_max = life_stage_config["max"]

    # Get activity adjustment
    activity_factor = settings.activity_adjustment[activity]["factor"]

    # Calculate MER with life stage and activity
    rec_cal = rer * life_stage_rec * activity_factor

    # Safety floor: minimum is always 0.7 × current weight RER
    safety_floor = current_rer * settings.constants["minimum_calorie_floor"]

    # If recommended falls below safety floor, use floor for both min and recommended
    if rec_cal < safety_floor:
        min_cal = safety_floor
        rec_cal = safety_floor
    else:
        min_cal = safety_floor

    return {
        "current_weight_kg": round(weight_kg, 2),
        "ideal_weight_kg": round(ideal_weight, 2),
        "bcs": bcs,
        "rer": round(rer),
        "life_stage_factor": life_stage_rec,
        "activity_factor": activity_factor,
        "calories": {
            "min": round(min_cal),
            "recommended": round(rec_cal)
        }
    }


def convert_weight(weight: float, from_unit: str) -> dict:
    """
    Convert weight between kg and lb

    Args:
        weight: Weight value to convert
        from_unit: Source unit ('kg' or 'lb')

    Returns:
        Dictionary with weight_kg, weight_lb, and from_unit
    """
    if from_unit.lower() == "kg":
        weight_kg = weight
        weight_lb = kg_to_lb(weight)
    else:  # lb
        weight_lb = weight
        weight_kg = lb_to_kg(weight)

    return {
        "weight_kg": round(weight_kg, 2),
        "weight_lb": round(weight_lb, 2),
        "from_unit": from_unit.lower()
    }
