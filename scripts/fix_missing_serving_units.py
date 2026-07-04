#!/usr/bin/env python3
"""
Fix wet food products with missing serving_unit by using size data
"""
import sqlite3

DB_PATH = "../data/catfood.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all wet food products with NULL or empty serving_unit
    cursor.execute("""
        SELECT p.id, p.name, n.serving_unit
        FROM products p
        JOIN nutrition n ON p.id = n.product_id
        WHERE p.type = 'wet'
          AND (n.serving_unit IS NULL OR n.serving_unit = '')
        ORDER BY p.id
    """)

    products = cursor.fetchall()
    print(f"Found {len(products)} wet food products with missing serving_unit")

    updated = 0
    skipped = 0

    for product in products:
        product_id = product['id']

        # Get size information for this product
        cursor.execute("""
            SELECT label, grams
            FROM sizes
            WHERE product_id = ?
            LIMIT 1
        """, (product_id,))

        size = cursor.fetchone()

        if not size or not size['label']:
            print(f"SKIP product {product_id}: No size data")
            skipped += 1
            continue

        # Create serving_unit from size label
        can_size = size['label']
        serving_unit = f"{can_size} can"

        # Update nutrition table
        cursor.execute("""
            UPDATE nutrition
            SET serving_unit = ?
            WHERE product_id = ?
        """, (serving_unit, product_id))

        updated += 1
        print(f"FIXED product {product_id}: serving_unit = '{serving_unit}'")

    conn.commit()
    conn.close()

    print(f"\nDone!")
    print(f"Updated: {updated} products")
    print(f"Skipped: {skipped} products (no size data)")

if __name__ == "__main__":
    main()
