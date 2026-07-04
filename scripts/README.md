# Data Collection Scripts

This directory contains scripts for collecting cat food nutrition data.

## Scrapers

### `petfood_scraper.py` - Full Production Scraper

Scrapes complete cat food nutrition database from petfood.express.

**What it collects:**
- Product names, brands, and URLs
- Guaranteed Analysis nutrition data (protein, fat, fiber, moisture, ash, taurine)
- Calorie information (when available)
- Available package sizes
- Wet/dry classification

**Output:**
- Database: `data/catfood.db` (SQLite)
- Cache: `cache/` (HTML/XML files for re-runs)

**Usage:**
```bash
cd /path/to/cat_weightloss
python scripts/petfood_scraper.py
```

**Runtime:** ~50-85 minutes (respects 3-second polite delay)

**Stats:**
- ~2,878 total products
- ~1,013 cat food products

---

### `test_scraper.py` - Test Version

Quick test version that scrapes only 5 products from one brand.

**Configuration:**
- `TEST_BRAND = "Wellness"` - Change to test different brands
- `MAX_PRODUCTS = 5` - Number of products to scrape

**Usage:**
```bash
python scripts/test_scraper.py
```

**Runtime:** ~30 seconds

---

## Database Schema

### Tables

**products**
- `id` - Primary key
- `url` - Product page URL (unique)
- `brand` - Brand name
- `name` - Product name
- `type` - 'wet' or 'dry' (based on moisture %)

**nutrition**
- `product_id` - Foreign key to products
- `ga_basis` - 'guaranteed' or 'typical'
- `kcal_per_kg` - Calories per kilogram
- `kcal_per_serving` - Calories per serving
- `serving_unit` - Serving unit (can, cup, oz, etc.)
- `protein_pct` - Protein %
- `fat_pct` - Fat %
- `fiber_pct` - Fiber %
- `moisture_pct` - Moisture %
- `ash_pct` - Ash %
- `taurine_pct` - Taurine %

**sizes**
- `product_id` - Foreign key to products
- `label` - Size label (e.g., "3 oz", "5.5 oz")
- `grams` - Normalized weight in grams
- `kcal` - Calculated calories for this size

### Views

**nutrition_dm**
- Dry-matter nutrition values (makes wet & dry foods comparable)
- Converts as-fed percentages to dry-matter basis

---

## Requirements

```bash
pip install requests beautifulsoup4 lxml
```

---

## Notes

- **Polite scraping:** 3-second delay between requests
- **Caching:** HTML pages cached to avoid re-fetching
- **Robots.txt:** Read https://www.petfood.express/robots.txt before running
- **Terms of Use:** Respect site's terms of service
- **Missing data:** Some products lack calorie info (stored as NULL for backfill)
