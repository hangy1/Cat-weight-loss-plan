# Cat Weight Loss Plan 🐱

A complete cat food meal planning system with calorie tracking and nutrition analysis. Built with FastAPI backend and React TypeScript frontend.

## 📋 Table of Contents
- [Features](#features)
- [Quick Start](#quick-start)
- [Meal Planner Usage](#meal-planner-usage)
- [API Reference](#api-reference)
- [Database](#database)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

## ✨ Features

### 🍽️ Meal Planner
- **Smart Food Search** - Autocomplete dropdown with food details and can sizes
- **Unit Validation** - Dry food (grams/cup) vs Wet food (grams/oz/can)
- **Mixed Meals** - Combine wet and dry foods in one plan
- **Nutrition Tracking** - Calories, protein, fat, moisture per food
- **Visual Summary** - Total calories with wet/dry composition breakdown

### 📊 Calorie Calculator
- Calculate daily calorie needs based on:
  - Current weight and body condition score (BCS)
  - Neutered status and activity level
  - Weight loss goals

### 🔍 Food Database
- **692 total cat food products**
- Dry and wet food options
- Detailed nutrition information (protein, fat, fiber, moisture, taurine)
- Multiple can/package sizes
- Major brands: Hill's, Wellness, Tiki Cat, Weruva, and more

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+
- npm or yarn

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/hangy1/Cat-weight-loss-plan.git
cd Cat-weight-loss-plan
```

2. **Install backend dependencies**
```bash
pip install -r requirements.txt
```

3. **Install frontend dependencies**
```bash
cd frontend
npm install
```

### Running the Application

**Terminal 1 - Backend API**
```bash
# From project root
uvicorn main:app --reload
```
✓ Backend running at: http://localhost:8000
✓ API docs at: http://localhost:8000/docs

**Terminal 2 - Frontend**
```bash
cd frontend
npm run dev
```
✓ Frontend running at: http://localhost:5173

## 🍽️ Meal Planner Usage

### Step 1: Calculate Daily Calorie Target
1. Open http://localhost:5173
2. Click **"📊 Calorie Calculator"** tab
3. Enter cat's weight (e.g., 10 lb), BCS (e.g., 7 for overweight)
4. Select neutered status and activity level
5. Click **Calculate**

Example: 10 lb cat with BCS 7 → **~210 kcal/day recommended**

### Step 2: Create Meal Plan
1. Click **"🍽️ Meal Planner"** tab
2. Search for foods (e.g., "Hill's Perfect Weight")
3. Select a food from dropdown
4. Enter amount and select unit
5. Click **Add to Meal**

#### Example Morning Meal (105 kcal)
```
Search: "Hill's Perfect Weight"
Select: Hill's Science Diet Perfect Weight Chicken Recipe (DRY)
Amount: 40
Unit: grams
```
✓ Shows: ~134.6 kcal, 16g protein

#### Example Evening Meal (110 kcal)
```
Search: "Wellness"
Select: Any wet food with can size shown
Amount: 1
Unit: can
```
✓ Shows: Nutrition based on specific can size (e.g., 3 oz can)

### Step 3: Review Totals
The **Meal Plan Summary** displays:
- Total Calories
- Total Weight (grams)
- Protein, Fat, Moisture totals
- Composition bar showing % Dry vs % Wet

## 🔌 API Reference

### Base URL
```
http://localhost:8000/api/catfood
```

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### 1. Search Foods
```bash
# Search by name
curl "http://localhost:8000/api/catfood/search?query=wellness&limit=5"

# Search dry foods only
curl "http://localhost:8000/api/catfood/search?food_type=dry&limit=5"

# Search by brand
curl "http://localhost:8000/api/catfood/search?brand=Hill's&limit=5"
```

#### 2. Get Food Details
```bash
curl "http://localhost:8000/api/catfood/55"
```

#### 3. Get Allowed Units
```bash
# Dry food units (returns: grams, cup)
curl "http://localhost:8000/api/catfood/units/dry"

# Wet food units (returns: grams, oz, can)
curl "http://localhost:8000/api/catfood/units/wet"
```

#### 4. Calculate Nutrition

**Dry Food - Half Cup:**
```bash
curl -X POST "http://localhost:8000/api/catfood/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 55,
    "amount": 0.5,
    "unit": "cup"
  }'
```

**Dry Food - 40 Grams:**
```bash
curl -X POST "http://localhost:8000/api/catfood/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 55,
    "amount": 40,
    "unit": "grams"
  }'
```

**Wet Food - 1 Can:**
```bash
curl -X POST "http://localhost:8000/api/catfood/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 8,
    "amount": 1,
    "unit": "can"
  }'
```

**Wet Food - 3 oz (weight):**
```bash
curl -X POST "http://localhost:8000/api/catfood/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 8,
    "amount": 3,
    "unit": "oz"
  }'
```

### Unit Validation

The API enforces proper units for each food type:

- **DRY FOOD**: Only accepts `grams` or `cup`
- **WET FOOD**: Only accepts `grams`, `oz` (weight), or `can`
- **All oz = weight ounces, NOT fluid ounces**

Error responses provide helpful messages:
```json
{
  "detail": "For dry food, please use 'grams' or 'cup' (not oz)"
}
```

## 💾 Database

### Schema
- **products** - Food products (id, url, brand, name, type)
- **nutrition** - Nutrition data (protein, fat, fiber, moisture, calories)
- **sizes** - Available package sizes (label, grams, kcal)

### Location
```
data/catfood.db
```

### Statistics
- 692 total products
- 476 wet food products
- 215 dry food products
- Multiple can sizes: 2.8 oz, 3 oz, 5.5 oz, 6 oz, 12.5 oz, etc.

## 🛠️ Development

### Project Structure
```
cat_weightloss/
├── app/
│   ├── api/                  # API routes
│   ├── db/                   # Database queries
│   ├── schemas/              # Pydantic models
│   └── services/             # Business logic
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── api/              # API client
│   │   └── types/            # TypeScript types
│   └── package.json
├── scripts/
│   ├── petfood_scraper.py   # Web scraper
│   └── fix_*.py             # Database maintenance
├── data/
│   └── catfood.db           # SQLite database
├── main.py                  # FastAPI app
└── requirements.txt
```

### Running Tests
```bash
# Test the API
python test_catfood_api.py

# Test the scraper (limited)
cd scripts
python test_scraper.py
```

### Database Maintenance Scripts

**Fix missing calorie data:**
```bash
cd scripts
python fix_missing_kcal_per_kg.py
```

**Fix wet food serving units:**
```bash
cd scripts
python fix_missing_serving_units.py
```

**Split multi-size products:**
```bash
cd scripts
python fix_wet_food_can_sizes.py
```

### Web Scraping
The database is populated from petfood.express using:
```bash
cd scripts
python petfood_scraper.py
```

Features:
- Parses nutrition from guaranteed analysis
- Extracts calorie content (kcal/kg, kcal/serving)
- Identifies wet vs dry based on moisture content
- Handles multiple can/package sizes
- Caches pages to avoid re-downloading

## 🔍 Troubleshooting

### Backend Issues

**"Module not found" errors:**
```bash
pip install -r requirements.txt
```

**Database not found:**
```bash
# Database should be at: data/catfood.db
# If missing, you'll need to run the scraper or restore from backup
```

**API not responding:**
```bash
# Check if backend is running
curl http://localhost:8000/docs
```

### Frontend Issues

**"Failed to search foods":**
- Verify backend is running at http://localhost:8000
- Check browser console (F12) for errors
- Test API: http://localhost:8000/api/catfood/search?limit=5

**"No foods found":**
- Only foods with calorie data appear in search
- Try major brands: "Wellness", "Hill's", "Tiki Cat"
- Some products may need data backfilled

**Build errors:**
```bash
cd frontend
rm -rf node_modules
npm install
npm run build
```

### Common Issues

**Duplicate can sizes showing:**
- Fixed in latest version
- Can size now shows only if not in product name

**Wrong units showing in dropdown:**
- Ensure product `type` field is set (wet/dry)
- Fixed: NULL types now default to 'dry'

**Can size not showing:**
- Ensure `serving_unit` is populated
- Run: `python scripts/fix_missing_serving_units.py`

## 📖 Additional Documentation

- **CATFOOD_API_GUIDE.md** - Complete API and frontend integration guide
- **frontend/MEAL_PLANNER_GUIDE.md** - Detailed user guide

## ✨ Future Enhancements

Optional features to consider:
1. Save meal plans to localStorage or database
2. Add price tracking per meal
3. Export meal plans as PDF
4. Set protein/fat targets
5. Compare foods side-by-side
6. Track daily feeding history
7. Multi-cat household support

## 📝 License

This project is for personal use.

## 🙏 Acknowledgments

- Food data sourced from petfood.express
- Built with FastAPI, React, TypeScript, and SQLite

---

Enjoy planning balanced meals for your cat! 🐱💚
