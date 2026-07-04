# Quick Start - Cat Food Meal Planner

## ✅ What's Been Built

A complete cat food meal planning system with:

1. **Smart Food Search** - Autocomplete dropdown with food details
2. **Unit Validation** - Dry food (grams/cup) vs Wet food (grams/oz/can)
3. **Mixed Meals** - Combine wet and dry foods in one plan
4. **Nutrition Tracking** - Calories, protein, fat, moisture per food
5. **Visual Summary** - Total calories with wet/dry composition breakdown

## 🚀 Start the Application

### Terminal 1 - Backend
```bash
cd /Users/hangyin/Documents/cat_weightloss
uvicorn main:app --reload
```
✓ Backend running at: http://localhost:8000

### Terminal 2 - Frontend
```bash
cd /Users/hangyin/Documents/cat_weightloss/frontend
npm run dev
```
✓ Frontend running at: http://localhost:5173

## 📝 Test the Meal Planner

### 1. Open the App
- Go to http://localhost:5173
- Click the **"🍽️ Meal Planner"** tab

### 2. Add a Dry Food
```
Search: "Hill's Perfect Weight"
Select: Hill's Science Diet Perfect Weight... (DRY)
Amount: 40
Unit: grams
Click: Add to Meal
```
✓ Should show: ~134.6 kcal, 16g protein

### 3. Add a Wet Food
```
Search: "Wellness"
Select: Any wet food result
Amount: 1
Unit: can
Click: Add to Meal
```
✓ Should show: calculated nutrition based on can size

### 4. View Totals
Look at the **Meal Plan Summary** section:
- Total Calories
- Total Weight (grams)
- Protein, Fat, Moisture totals
- Composition bar showing % Dry vs % Wet

### 5. Test Unit Validation
```
Select a DRY food
Try to use unit: "oz"
```
❌ Should show error: "For dry food, please use 'grams' or 'cup' (not oz)"

```
Select a WET food
Try to use unit: "cup"
```
❌ Should show error: "For wet food, please use 'grams', 'oz' (weight), or 'can' only"

## 📊 Complete Workflow Example

### Step 1: Calculate Daily Target
```
1. Click "📊 Calorie Calculator" tab
2. Enter: Weight 10 lb, BCS 7 (overweight)
3. Select: Neutered Adult, Typical Activity
4. Click: Calculate
```
Result: **~210 kcal/day recommended**

### Step 2: Plan Meals
```
1. Click "🍽️ Meal Planner" tab
2. Create morning meal (105 kcal):
   - Add: Hill's Perfect Weight Dry, 30g → 100 kcal
3. Create evening meal (110 kcal):
   - Add: Wellness Pate Wet, 1 can → 107 kcal
```
Total Daily: 207 kcal ≈ 210 target ✓

## 🎯 Key Features to Test

### Search Autocomplete
- Type "Hill's" → Should show dropdown with results
- Type "Wellness" → Should filter to Wellness products
- Shows: Food name, type badge, calories, brand

### Dynamic Units
- Select dry food → Units show: grams, cup
- Select wet food → Units show: grams, oz (weight), can
- Shows note for wet: "oz = weight ounces (NOT fluid oz)"

### Meal Item Display
Each added food shows:
- Food type badge (🟤 DRY or 🔵 WET)
- Amount + unit (with grams equivalent)
- Calories (highlighted)
- Protein, fat, moisture in grams
- ✕ Remove button

### Composition Visualization
- Color-coded bar: [■■■ Dry ■■ Wet]
- Shows percentages: "64% Dry | 36% Wet"
- Based on calorie distribution

## 📁 Files Created

```
frontend/src/
├── components/
│   ├── CatFoodMealPlanner.tsx  ✓ Main component (400+ lines)
│   └── CatFoodMealPlanner.css  ✓ Complete styling
├── api/
│   └── catfood.ts              ✓ API client functions
├── types/
│   └── catfood.ts              ✓ TypeScript interfaces
├── App.tsx                     ✓ Updated with tabs
└── App.css                     ✓ Tab styles added
```

## 🔍 Troubleshooting

### "Failed to search foods"
- Check backend is running: http://localhost:8000/docs
- Verify API responds: http://localhost:8000/api/catfood/search?limit=5

### "No foods found"
- Only foods with calorie data appear (399/626 products)
- Try major brands: "Wellness", "Hill's", "Tiki Cat"
- Some products need calorie data backfilled

### Build Errors
```bash
cd frontend
npm install
npm run build
```
Should complete without errors

### Browser Console Errors
- Press F12 to open DevTools
- Check Console for error messages
- Verify API calls to localhost:8000

## 📖 Full Documentation

- **CATFOOD_API_GUIDE.md** - Complete API and frontend guide
- **API_QUICK_START.md** - API testing reference
- **frontend/MEAL_PLANNER_GUIDE.md** - Detailed user guide

## ✨ What's Next?

The meal planner is production-ready! Optional enhancements:
1. Save meal plans to localStorage
2. Add price tracking per meal
3. Export meal plans as PDF
4. Set protein/fat targets
5. Compare foods side-by-side

Enjoy planning balanced meals for your cat! 🐱
