#!/usr/bin/env python3
"""
Quick test to create and populate the database with sample data
"""

import sqlite3
from pathlib import Path

DB_PATH = "data/catfood_test.db"

# Schema from the main scraper
SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id    INTEGER PRIMARY KEY,
    url   TEXT UNIQUE,
    brand TEXT,
    name  TEXT,
    type  TEXT CHECK (type IN ('wet','dry') OR type IS NULL)
);

CREATE TABLE IF NOT EXISTS nutrition (
    product_id       INTEGER PRIMARY KEY REFERENCES products(id) ON DELETE CASCADE,
    ga_basis         TEXT,            -- 'guaranteed' (min/max) or 'typical'
    kcal_per_kg      REAL,            -- NULL if not printed on page
    kcal_per_serving REAL,            -- NULL if not printed on page
    serving_unit     TEXT,            -- can / cup / oz / pouch ...
    protein_pct      REAL,            -- %  (min if guaranteed, else typical)
    fat_pct          REAL,            -- %
    fiber_pct        REAL,            -- %
    moisture_pct     REAL,            -- %
    ash_pct          REAL,            -- %  (often absent)
    taurine_pct      REAL             -- %  (often absent)
);

CREATE TABLE IF NOT EXISTS sizes (
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    label      TEXT,                 -- raw label, e.g. '5.5 oz', '12 lb'
    grams      REAL,                 -- normalized weight, for kcal math
    kcal       REAL,                 -- kcal_per_kg * grams/1000, or NULL
    PRIMARY KEY (product_id, label)
);

-- Dry-matter view: makes wet & dry foods comparable.
-- DM% = as_fed% / (100 - moisture%) * 100
CREATE VIEW IF NOT EXISTS nutrition_dm AS
SELECT
    p.id, p.brand, p.name, p.type,
    n.ga_basis, n.kcal_per_kg, n.kcal_per_serving, n.serving_unit,
    n.moisture_pct,
    ROUND(n.protein_pct * 100.0 / NULLIF(100 - n.moisture_pct, 0), 1) AS protein_dm,
    ROUND(n.fat_pct     * 100.0 / NULLIF(100 - n.moisture_pct, 0), 1) AS fat_dm,
    ROUND(n.fiber_pct   * 100.0 / NULLIF(100 - n.moisture_pct, 0), 1) AS fiber_dm
FROM products p JOIN nutrition n ON n.product_id = p.id;
"""

# Sample data from the test run
SAMPLE_PRODUCTS = [
    {
        "url": "https://www.petfood.express/products/wellness-complete-health-pate-turkey-salmon-canned-cat-food.html",
        "brand": "Wellness Pet Company",
        "name": "Wellness Complete Health Pate Turkey & Salmon Canned Cat Food",
        "type": "wet",
        "ga_basis": "guaranteed",
        "kcal_per_kg": None,
        "kcal_per_serving": None,
        "serving_unit": None,
        "protein_pct": 10.5,
        "fat_pct": 5.0,
        "fiber_pct": 1.0,
        "moisture_pct": 78.0,
        "ash_pct": None,
        "taurine_pct": 0.1,
        "sizes": [
            {"label": "3 oz", "grams": 85.0, "kcal": None},
            {"label": "5.5 oz", "grams": 155.9, "kcal": None},
            {"label": "12.5 oz", "grams": 354.4, "kcal": None}
        ]
    },
    {
        "url": "https://www.petfood.express/products/wellness-complete-health-grain-free-chicken-turkey-pate-favorites-variety-pack-canned-cat-food.html",
        "brand": "Wellness Pet Company",
        "name": "Wellness Complete Health Grain Free Chicken & Turkey Pate Favorites Variety Pack Canned Cat Food",
        "type": "wet",
        "ga_basis": "guaranteed",
        "kcal_per_kg": 1166.0,
        "kcal_per_serving": 156.0,
        "serving_unit": "can",
        "protein_pct": 10.5,
        "fat_pct": 5.0,
        "fiber_pct": 1.0,
        "moisture_pct": 78.0,
        "ash_pct": None,
        "taurine_pct": 0.1,
        "sizes": []
    },
    {
        "url": "https://www.petfood.express/products/wellness-morsels-w-chicken-chicken-liver-in-savory-sauce-adult-wet-cat-food.html",
        "brand": "Wellness Pet Company",
        "name": "Wellness Morsels w/ Chicken & Chicken Liver in Savory Sauce Adult Wet Cat Food",
        "type": "wet",
        "ga_basis": "guaranteed",
        "kcal_per_kg": 725.0,
        "kcal_per_serving": 62.0,
        "serving_unit": "oz",
        "protein_pct": 7.0,
        "fat_pct": 4.0,
        "fiber_pct": 1.0,
        "moisture_pct": 82.0,
        "ash_pct": 2.0,
        "taurine_pct": 0.1,
        "sizes": [
            {"label": "3 oz", "grams": 85.0, "kcal": 61.6}
        ]
    }
]


def main():
    # Delete old database
    db_path = Path(DB_PATH)
    if db_path.exists():
        db_path.unlink()

    # Create database
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.commit()

    print(f"Created database: {DB_PATH}\n")

    # Insert sample data
    for product in SAMPLE_PRODUCTS:
        # Insert product
        cur = conn.execute(
            """INSERT INTO products (url, brand, name, type) VALUES (?,?,?,?)
               RETURNING id""",
            (product["url"], product["brand"], product["name"], product["type"]),
        )
        pid = cur.fetchone()[0]

        # Insert nutrition
        conn.execute(
            """INSERT INTO nutrition
               (product_id, ga_basis, kcal_per_kg, kcal_per_serving, serving_unit,
                protein_pct, fat_pct, fiber_pct, moisture_pct, ash_pct, taurine_pct)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (pid, product["ga_basis"], product["kcal_per_kg"], product["kcal_per_serving"],
             product["serving_unit"], product["protein_pct"], product["fat_pct"],
             product["fiber_pct"], product["moisture_pct"], product["ash_pct"],
             product["taurine_pct"]),
        )

        # Insert sizes
        for size in product["sizes"]:
            conn.execute(
                "INSERT INTO sizes (product_id, label, grams, kcal) VALUES (?,?,?,?)",
                (pid, size["label"], size["grams"], size["kcal"]),
            )

        conn.commit()
        print(f"✓ Inserted: {product['name'][:70]}")

    print(f"\n✓ Database created with {len(SAMPLE_PRODUCTS)} sample products")
    conn.close()


if __name__ == "__main__":
    main()
