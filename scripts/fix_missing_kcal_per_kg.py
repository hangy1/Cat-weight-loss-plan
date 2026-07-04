#!/usr/bin/env python3
"""
Fix products that have kcal_per_serving but missing kcal_per_kg
Calculate kcal_per_kg from serving data and size information
"""
import sqlite3

DB_PATH = "../data/catfood.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all products with kcal_per_serving but no kcal_per_kg
    cursor.execute("""
        SELECT
            p.id,
            p.name,
            p.type,
            n.kcal_per_serving,
            n.serving_unit
        FROM products p
        JOIN nutrition n ON p.id = n.product_id
        WHERE n.kcal_per_serving IS NOT NULL
          AND n.kcal_per_kg IS NULL
        ORDER BY p.id
    """)

    products = cursor.fetchall()
    print(f"Found {len(products)} products missing kcal_per_kg")

    fixed = 0
    skipped = 0

    for product in products:
        product_id = product['id']

        # Get size information for this product
        cursor.execute("""
            SELECT label, grams, kcal
            FROM sizes
            WHERE product_id = ?
            LIMIT 1
        """, (product_id,))

        size = cursor.fetchone()

        if not size or not size['grams']:
            print(f"SKIP product {product_id}: No size/grams data")
            skipped += 1
            continue

        # Calculate kcal_per_kg from kcal_per_serving and grams
        grams = size['grams']
        kcal_per_serving = product['kcal_per_serving']
        kcal_per_kg = round((kcal_per_serving / grams) * 1000, 2)

        # Update nutrition table
        cursor.execute("""
            UPDATE nutrition
            SET kcal_per_kg = ?
            WHERE product_id = ?
        """, (kcal_per_kg, product_id))

        # Update sizes table with kcal if missing
        if not size['kcal']:
            cursor.execute("""
                UPDATE sizes
                SET kcal = ?
                WHERE product_id = ? AND label = ?
            """, (kcal_per_serving, product_id, size['label']))

        fixed += 1
        print(f"FIXED product {product_id}: {kcal_per_serving} kcal / {grams}g = {kcal_per_kg} kcal/kg")

    conn.commit()
    conn.close()

    print(f"\nDone!")
    print(f"Fixed: {fixed} products")
    print(f"Skipped: {skipped} products (no size data)")

if __name__ == "__main__":
    main()
