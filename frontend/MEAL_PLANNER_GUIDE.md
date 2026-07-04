# Cat Food Meal Planner - Frontend Guide

## Features

The meal planner allows you to:

1. **Search for Cat Foods** - Search by brand or product name with autocomplete dropdown
2. **Select Appropriate Units** - Units automatically adjust based on food type:
   - **Dry Food**: grams or cups only
   - **Wet Food**: grams, oz (weight), or cans only
3. **Mix Wet & Dry Foods** - Add both types to create a complete meal plan
4. **Track Nutrition** - See calories, protein, fat, and moisture for each food
5. **View Totals** - Get complete meal plan summary with composition breakdown

## How to Use

### 1. Start the Backend Server

First, make sure your FastAPI backend is running:

```bash
cd /Users/hangyin/Documents/cat_weightloss
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

### 2. Start the Frontend

In a new terminal, start the React development server:

```bash
cd frontend
npm run dev
```

The app will be available at http://localhost:5173

### 3. Using the Meal Planner

1. **Navigate to Meal Planner Tab**
   - Click on the "🍽️ Meal Planner" tab

2. **Search for a Food**
   - Type in the search box (e.g., "Wellness", "Hill's")
   - Select a food from the dropdown results
   - Only foods with calorie data will be shown

3. **Enter Amount**
   - Enter the amount you want to feed
   - Select the appropriate unit:
     - For dry food: grams or cup
     - For wet food: grams, oz (weight), or can
   - Note: oz = weight ounces, NOT fluid ounces

4. **Add to Meal Plan**
   - Click "Add to Meal" button
   - The food will be added with calculated nutrition

5. **Add More Foods**
   - Repeat steps 2-4 to add more foods
   - You can mix wet and dry foods!

6. **View Summary**
   - See total calories, protein, fat, and weight
   - View wet/dry food composition percentage
   - Compare against your cat's daily calorie target from the calculator

7. **Remove Foods**
   - Click the ✕ button on any food item to remove it

## Example Meal Plans

### Mixed Diet (Wet + Dry)
```
Dry Food:
- Hill's Perfect Weight: 40g (134.6 kcal)

Wet Food:
- Wellness Complete Health Pate: 1 can (107 kcal)

Total: 241.6 kcal
```

### All Wet Food
```
- Tiki Cat Velvet Mousse: 1 can (60 kcal)
- Weruva Paw Lickin' Chicken: 1 can (70 kcal)
- Wellness Pate: 3 oz (80 kcal)

Total: 210 kcal
```

### All Dry Food
```
- Hill's Perfect Weight: 0.5 cup (157.5 kcal)
- Wellness Core Grain-Free: 20g (67 kcal)

Total: 224.5 kcal
```

## Tips

1. **Calculate Daily Target First**
   - Use the Calorie Calculator tab to determine your cat's daily calorie needs
   - Then use the Meal Planner to create meals that meet that target

2. **Portion Control**
   - Split the daily calorie target into 2-3 meals
   - Example: If target is 240 kcal/day, create 2 meals of 120 kcal each

3. **Unit Conversions**
   - The system shows grams equivalent for all servings
   - Use this to measure portions accurately with a kitchen scale

4. **Mix Wet & Dry**
   - Many cats prefer a mix of textures
   - Wet food adds moisture to the diet
   - Dry food is convenient and helps dental health

5. **Save Your Plans**
   - Take screenshots of successful meal plans
   - Or write down the portions that work well

## Troubleshooting

### "No foods found with calorie data"
- Some foods in the database don't have calorie information
- Try searching for a different brand or product
- Run the scraper again to update missing data

### "For dry food, please use 'grams' or 'cup' (not oz)"
- You selected a dry food but tried to use oz or can
- Change the unit to grams or cup

### "For wet food, please use 'grams', 'oz', or 'can' (not cup)"
- You selected a wet food but tried to use cup
- Change the unit to grams, oz, or can

### Search not working
- Make sure the backend server is running on http://localhost:8000
- Check the browser console for errors
- Verify the API is accessible at http://localhost:8000/docs

## Database Information

- **626 cat food products** available
- **399 products with calorie data** (searchable)
- **227 products missing calories** (can be backfilled)

Products include major brands like:
- Wellness
- Hill's Science Diet
- Tiki Cat
- Weruva
- ZIWI Peak
- Open Farm
- Applaws
- RAWZ
