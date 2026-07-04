"""
Cat Food API Routes
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.db.catfood import (
    search_foods,
    get_food_by_id,
    get_food_sizes,
    get_brands,
    get_dry_matter_nutrition
)
from app.schemas.catfood import (
    FoodSearchResult,
    FoodDetail,
    DryMatterNutrition,
    ServingCalculationRequest,
    ServingCalculationResponse
)
from app.services.catfood_calculator import (
    convert_to_grams,
    calculate_nutrition,
    get_allowed_units
)

router = APIRouter(prefix="/catfood", tags=["Cat Food"])


@router.get("/search", response_model=List[FoodSearchResult])
def search_cat_foods(
    query: str = Query("", description="Search by product name"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    food_type: Optional[str] = Query(None, description="Filter by type: 'wet' or 'dry'"),
    limit: int = Query(50, ge=1, le=200, description="Max results")
):
    """
    Search cat foods by name, brand, or type

    Examples:
    - /catfood/search?query=wellness
    - /catfood/search?brand=Hill's
    - /catfood/search?food_type=wet
    """
    try:
        results = search_foods(query, brand, food_type, limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/brands", response_model=List[str])
def get_all_brands():
    """Get list of all available brands"""
    try:
        return get_brands()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/units/{food_type}", response_model=dict)
def get_units_for_food_type(food_type: str):
    """
    Get allowed units for a food type

    Args:
        food_type: 'wet' or 'dry'

    Returns:
        Dictionary with allowed units and conversion info
    """
    if food_type not in ['wet', 'dry']:
        raise HTTPException(
            status_code=400,
            detail="food_type must be 'wet' or 'dry'"
        )

    units = get_allowed_units(food_type)

    return {
        "food_type": food_type,
        "allowed_units": units,
        "note": "oz = weight ounces (NOT fluid oz)" if food_type == "wet" else None
    }


@router.get("/{product_id}", response_model=FoodDetail)
def get_food_detail(product_id: int):
    """Get detailed information about a specific food product"""
    try:
        food = get_food_by_id(product_id)
        if not food:
            raise HTTPException(status_code=404, detail="Product not found")

        # Get available sizes
        sizes = get_food_sizes(product_id)
        food['sizes'] = sizes

        return food
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{product_id}/dry-matter", response_model=DryMatterNutrition)
def get_food_dry_matter(product_id: int):
    """Get dry matter nutrition (comparable across wet/dry foods)"""
    try:
        dm_nutrition = get_dry_matter_nutrition(product_id)
        if not dm_nutrition:
            raise HTTPException(status_code=404, detail="Product not found")

        return dm_nutrition
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calculate", response_model=ServingCalculationResponse)
def calculate_serving_nutrition(request: ServingCalculationRequest):
    """
    Calculate nutrition for a serving amount

    DRY FOOD: use 'grams' or 'cup'
    WET FOOD: use 'grams', 'oz' (weight), or 'can'

    Example requests:
    - Dry food: {"product_id": 55, "amount": 0.5, "unit": "cup"}
    - Wet food: {"product_id": 84, "amount": 3, "unit": "oz"}
    - Wet food: {"product_id": 84, "amount": 1, "unit": "can"}
    """
    try:
        # Get product info
        food = get_food_by_id(request.product_id)
        if not food:
            raise HTTPException(status_code=404, detail="Product not found")

        # Convert to grams
        grams, error = convert_to_grams(
            amount=request.amount,
            unit=request.unit,
            food_type=food.get('type'),
            serving_unit=food.get('serving_unit'),
            kcal_per_serving=food.get('kcal_per_serving'),
            kcal_per_kg=food.get('kcal_per_kg')
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        # Calculate nutrition
        nutrition = calculate_nutrition(
            grams=grams,
            protein_pct=food.get('protein_pct'),
            fat_pct=food.get('fat_pct'),
            fiber_pct=food.get('fiber_pct'),
            moisture_pct=food.get('moisture_pct'),
            kcal_per_kg=food.get('kcal_per_kg')
        )

        return ServingCalculationResponse(
            product_id=request.product_id,
            product_name=food['name'],
            amount=request.amount,
            unit=request.unit,
            grams=round(grams, 1),
            calories=nutrition['calories'],
            protein_g=nutrition['protein_g'],
            fat_g=nutrition['fat_g'],
            fiber_g=nutrition['fiber_g'],
            moisture_g=nutrition['moisture_g'],
            protein_pct=food.get('protein_pct'),
            fat_pct=food.get('fat_pct'),
            fiber_pct=food.get('fiber_pct'),
            moisture_pct=food.get('moisture_pct')
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
