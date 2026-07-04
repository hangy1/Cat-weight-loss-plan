# Cat Food API Quick Start

## Start the Server

```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Quick Test Commands

### 1. Search for Foods

```bash
# Search by name
curl "http://localhost:8000/api/catfood/search?query=wellness&limit=5"

# Search dry foods
curl "http://localhost:8000/api/catfood/search?food_type=dry&limit=5"

# Search by brand
curl "http://localhost:8000/api/catfood/search?brand=Hill's&limit=5"
```

### 2. Get Allowed Units

```bash
# Dry food units (returns: grams, cup)
curl "http://localhost:8000/api/catfood/units/dry"

# Wet food units (returns: grams, oz, can)
curl "http://localhost:8000/api/catfood/units/wet"
```

### 3. Get Food Details

```bash
# Get product ID 55 (Hill's Perfect Weight - dry)
curl "http://localhost:8000/api/catfood/55"
```

### 4. Calculate Nutrition

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
    "product_id": 1,
    "amount": 1,
    "unit": "can"
  }'
```

**Wet Food - 3 oz (weight):**
```bash
curl -X POST "http://localhost:8000/api/catfood/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "amount": 3,
    "unit": "oz"
  }'
```

### 5. Test Error Handling

**Wrong unit for dry food (will return 400 error):**
```bash
curl -X POST "http://localhost:8000/api/catfood/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 55,
    "amount": 3,
    "unit": "oz"
  }'
```

Expected response:
```json
{
  "detail": "For dry food, please use 'grams' or 'cup' (not oz)"
}
```

**Wrong unit for wet food (will return 400 error):**
```bash
curl -X POST "http://localhost:8000/api/catfood/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "amount": 0.5,
    "unit": "cup"
  }'
```

Expected response:
```json
{
  "detail": "For wet food, please use 'grams', 'oz' (weight), or 'can' only (not 'cup')"
}
```

## Database Stats

- **626 total cat food products**
- **399 products with calorie data** (64%)
- **227 products missing calories** (can be backfilled by re-running scraper with fixes)

## Frontend Integration

See `CATFOOD_API_GUIDE.md` for detailed frontend integration examples with JavaScript/React.

## Important Notes

- **DRY FOOD**: Only use `grams` or `cup`
- **WET FOOD**: Only use `grams`, `oz` (weight), or `can`
- **All oz = weight ounces, NOT fluid ounces**
- The API enforces these rules and returns helpful error messages
