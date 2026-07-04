#!/usr/bin/env python3
"""
Test script for cat food calculator
Demonstrates the API functionality without running the full server
"""

from app.db.catfood import search_foods, get_food_by_id
from app.services.catfood_calculator import convert_to_grams, calculate_nutrition, get_allowed_units

print("="*80)
print("CAT FOOD CALCULATOR TEST")
print("="*80)

# 1. Search for foods
print("\n1. Searching for 'Hill's Perfect Weight'...")
results = search_foods(query="Perfect Weight", brand="Hill", limit=3)
print(f"Found {len(results)} results:")
for food in results:
    print(f"  - [{food['id']}] {food['name']}")
    print(f"    Type: {food['type']}, kcal/kg: {food['kcal_per_kg']}")

# 2. Get food details
if results:
    food_id = results[0]['id']
    print(f"\n2. Getting details for product ID {food_id}...")
    food = get_food_by_id(food_id)
    print(f"  Name: {food['name']}")
    print(f"  Type: {food['type']}")
    print(f"  Protein: {food['protein_pct']}%")
    print(f"  Fat: {food['fat_pct']}%")
    print(f"  Moisture: {food['moisture_pct']}%")
    print(f"  Calories: {food['kcal_per_kg']} kcal/kg")
    print(f"  Serving: {food['kcal_per_serving']} kcal/{food['serving_unit']}")

    # 3. Check allowed units
    print(f"\n3. Allowed units for {food['type']} food:")
    units = get_allowed_units(food['type'])
    print(f"  {units}")

    # 4. Test dry food calculations
    if food['type'] == 'dry':
        print("\n4. DRY FOOD CALCULATIONS:")

        # Test with cup
        print("\n  a) 0.5 cup:")
        grams, error = convert_to_grams(0.5, 'cup', food_type='dry')
        if error:
            print(f"     ERROR: {error}")
        else:
            nutrition = calculate_nutrition(
                grams, food['protein_pct'], food['fat_pct'],
                food['fiber_pct'], food['moisture_pct'], food['kcal_per_kg']
            )
            print(f"     = {grams}g")
            print(f"     Calories: {nutrition['calories']} kcal")
            print(f"     Protein: {nutrition['protein_g']}g")
            print(f"     Fat: {nutrition['fat_g']}g")

        # Test with grams
        print("\n  b) 40 grams:")
        grams, error = convert_to_grams(40, 'grams', food_type='dry')
        nutrition = calculate_nutrition(
            grams, food['protein_pct'], food['fat_pct'],
            food['fiber_pct'], food['moisture_pct'], food['kcal_per_kg']
        )
        print(f"     Calories: {nutrition['calories']} kcal")
        print(f"     Protein: {nutrition['protein_g']}g")

        # Test invalid unit for dry
        print("\n  c) Try invalid unit 'oz' for dry food:")
        grams, error = convert_to_grams(3, 'oz', food_type='dry')
        if error:
            print(f"     ✓ Correctly rejected: {error}")

# 5. Test wet food
print("\n5. Testing WET FOOD...")
wet_results = search_foods(food_type='wet', limit=1)
if wet_results:
    wet_food = get_food_by_id(wet_results[0]['id'])
    print(f"  Food: {wet_food['name']}")
    print(f"  Serving: {wet_food['serving_unit']}")

    print("\n  WET FOOD CALCULATIONS:")

    # Test with can
    print(f"\n  a) 1 can ({wet_food['serving_unit']}):")
    grams, error = convert_to_grams(
        1, 'can', food_type='wet',
        serving_unit=wet_food['serving_unit'],
        kcal_per_serving=wet_food['kcal_per_serving'],
        kcal_per_kg=wet_food['kcal_per_kg']
    )
    if error:
        print(f"     ERROR: {error}")
    else:
        nutrition = calculate_nutrition(
            grams, wet_food['protein_pct'], wet_food['fat_pct'],
            wet_food['fiber_pct'], wet_food['moisture_pct'], wet_food['kcal_per_kg']
        )
        print(f"     = {grams}g")
        print(f"     Calories: {nutrition['calories']} kcal")
        print(f"     Protein: {nutrition['protein_g']}g")
        print(f"     Moisture: {nutrition['moisture_g']}g")

    # Test with oz (weight)
    print("\n  b) 3 oz (weight, not fluid):")
    grams, error = convert_to_grams(3, 'oz', food_type='wet')
    nutrition = calculate_nutrition(
        grams, wet_food['protein_pct'], wet_food['fat_pct'],
        wet_food['fiber_pct'], wet_food['moisture_pct'], wet_food['kcal_per_kg']
    )
    print(f"     = {grams}g")
    print(f"     Calories: {nutrition['calories']} kcal")

    # Test invalid unit for wet
    print("\n  c) Try invalid unit 'cup' for wet food:")
    grams, error = convert_to_grams(0.5, 'cup', food_type='wet')
    if error:
        print(f"     ✓ Correctly rejected: {error}")

print("\n" + "="*80)
print("✓ Test complete! The API is ready to use.")
print("="*80)
