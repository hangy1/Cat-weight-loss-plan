"""
Cat food nutrition calculator service
Handles unit conversions and nutrition calculations

IMPORTANT: All weights are in ounces (oz) by weight, NOT fluid ounces (fl oz)
- Dry food: grams or cups only
- Wet food: grams, oz (weight), or cans only
"""
from typing import Optional, Tuple


# Standard conversion factors
GRAMS_PER_OZ = 28.3495  # Weight ounces, NOT fluid ounces

# Standard dry food cup weight (varies by brand, but this is typical)
# User can override this if they know their specific food's cup weight
DEFAULT_GRAMS_PER_CUP_DRY = 100.0  # typical for dry kibble


def parse_unit(unit: str) -> str:
    """Normalize unit string to standard format"""
    unit = unit.lower().strip()

    # Map common variations
    unit_map = {
        'g': 'grams',
        'gram': 'grams',
        'grams': 'grams',
        'oz': 'oz',  # WEIGHT ounces only
        'ounce': 'oz',
        'ounces': 'oz',
        'cup': 'cup',
        'cups': 'cup',
        'c': 'cup',
        'can': 'can',
        'cans': 'can',
    }

    return unit_map.get(unit, unit)


def get_allowed_units(food_type: str) -> list:
    """
    Get allowed units for a food type

    Args:
        food_type: 'wet' or 'dry'

    Returns:
        List of allowed unit strings
    """
    if food_type == 'dry':
        return ['grams', 'cup']
    elif food_type == 'wet':
        return ['grams', 'oz', 'can']
    else:
        # Unknown type, allow all
        return ['grams', 'oz', 'cup', 'can']


def validate_unit_for_food_type(unit: str, food_type: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate that unit is allowed for the food type

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not food_type:
        return True, None

    unit = parse_unit(unit)
    allowed = get_allowed_units(food_type)

    if unit not in allowed:
        if food_type == 'dry':
            return False, f"For dry food, please use 'grams' or 'cup' only (not '{unit}')"
        elif food_type == 'wet':
            return False, f"For wet food, please use 'grams', 'oz' (weight), or 'can' only (not '{unit}')"

    return True, None


def convert_to_grams(
    amount: float,
    unit: str,
    food_type: Optional[str] = None,
    serving_unit: Optional[str] = None,
    kcal_per_serving: Optional[float] = None,
    kcal_per_kg: Optional[float] = None,
    grams_per_cup: Optional[float] = None
) -> Tuple[float, Optional[str]]:
    """
    Convert serving amount to grams

    DRY FOOD: accepts grams, cup
    WET FOOD: accepts grams, oz (weight), can

    Args:
        amount: Amount to convert
        unit: Unit of amount
        food_type: 'wet' or 'dry'
        serving_unit: Product's serving unit (e.g., "3 oz can", "8 oz cup")
        kcal_per_serving: Calories per serving from database
        kcal_per_kg: Calories per kg from database
        grams_per_cup: Specific grams per cup for this product

    Returns:
        Tuple of (grams, error_message)
    """
    unit = parse_unit(unit)

    # Validate unit for food type
    is_valid, error_msg = validate_unit_for_food_type(unit, food_type)
    if not is_valid:
        return 0, error_msg

    # Direct conversion to grams
    if unit == 'grams':
        return amount, None

    # Ounces (WEIGHT, not fluid) - wet food only
    if unit == 'oz':
        if food_type == 'dry':
            return 0, "For dry food, please use 'grams' or 'cup' (not oz)"
        return amount * GRAMS_PER_OZ, None

    # Cup conversion - dry food only
    if unit == 'cup':
        if food_type == 'wet':
            return 0, "For wet food, please use 'grams', 'oz', or 'can' (not cup)"
        # Use product-specific grams per cup if available
        if grams_per_cup:
            return amount * grams_per_cup, None
        # Otherwise use default
        return amount * DEFAULT_GRAMS_PER_CUP_DRY, None

    # Can conversion - wet food only
    if unit == 'can':
        if food_type == 'dry':
            return 0, "For dry food, please use 'grams' or 'cup' (not can)"

        if not serving_unit:
            return 0, "Cannot convert 'can' without knowing can size. Please use grams or oz (weight)."

        # Try to parse can size from serving_unit
        # Examples: "3 oz can", "5.5 oz", "2.9 oz can"
        import re
        match = re.search(r'([\d.]+)\s*oz', serving_unit)
        if match:
            oz_per_can = float(match.group(1))
            grams = amount * oz_per_can * GRAMS_PER_OZ
            return grams, None

        # If we can't parse, try to calculate from calories
        if kcal_per_serving and kcal_per_kg:
            grams_per_can = (kcal_per_serving / kcal_per_kg) * 1000
            grams = amount * grams_per_can
            return grams, None

        return 0, f"Cannot parse can size from '{serving_unit}'. Please use grams or oz (weight)."

    return 0, f"Unknown unit: {unit}"


def calculate_nutrition(
    grams: float,
    protein_pct: Optional[float],
    fat_pct: Optional[float],
    fiber_pct: Optional[float],
    moisture_pct: Optional[float],
    kcal_per_kg: Optional[float]
) -> dict:
    """
    Calculate nutrition for a given amount in grams

    Returns:
        Dictionary with calculated nutrition values
    """
    result = {
        'calories': None,
        'protein_g': None,
        'fat_g': None,
        'fiber_g': None,
        'moisture_g': None,
    }

    if kcal_per_kg:
        result['calories'] = round((kcal_per_kg * grams / 1000), 1)

    if protein_pct:
        result['protein_g'] = round((protein_pct / 100) * grams, 1)

    if fat_pct:
        result['fat_g'] = round((fat_pct / 100) * grams, 1)

    if fiber_pct:
        result['fiber_g'] = round((fiber_pct / 100) * grams, 1)

    if moisture_pct:
        result['moisture_g'] = round((moisture_pct / 100) * grams, 1)

    return result
