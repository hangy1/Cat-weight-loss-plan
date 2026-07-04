#!/usr/bin/env python3
"""
Fix wet food can sizes - create separate products for each can size
"""
import sqlite3
import re

DB_PATH = "../data/catfood.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all wet food products with multiple sizes or incomplete serving_unit
    cursor.execute("""
        SELECT
            p.id,
            p.url,
            p.brand,
            p.name,
            p.type,
            n.ga_basis,
            n.kcal_per_kg,
            n.kcal_per_serving,
            n.serving_unit,
            n.protein_pct,
            n.fat_pct,
            n.fiber_pct,
            n.moisture_pct,
            n.ash_pct,
            n.taurine_pct
        FROM products p
        JOIN nutrition n ON p.id = n.product_id
        WHERE p.type = 'wet'
          AND n.kcal_per_serving IS NOT NULL
          AND p.id NOT IN (198, 627)
        ORDER BY p.id
    """)

    products = cursor.fetchall()

    processed = 0
    created = 0

    for product in products:
        product_id = product['id']

        # Get all sizes for this product
        cursor.execute("""
            SELECT label, grams, kcal
            FROM sizes
            WHERE product_id = ?
            ORDER BY grams
        """, (product_id,))

        sizes = cursor.fetchall()

        if not sizes:
            print(f"WARNING: No sizes found for product {product_id}: {product['name']}")
            continue

        # If only one size, just update the product name and serving_unit
        if len(sizes) == 1:
            size = sizes[0]
            can_size = size['label']

            # Update product name if it doesn't already include can size
            if f"({can_size} can)" not in product['name']:
                new_name = f"{product['name']} ({can_size} can)"
                cursor.execute("""
                    UPDATE products
                    SET name = ?
                    WHERE id = ?
                """, (new_name, product_id))

            # Update serving_unit
            cursor.execute("""
                UPDATE nutrition
                SET serving_unit = ?
                WHERE product_id = ?
            """, (f"{can_size} can", product_id))

            processed += 1
            print(f"UPDATED product {product_id}: {can_size} can")

        # If multiple sizes, create separate products for each
        else:
            print(f"\nProduct {product_id} has {len(sizes)} sizes: {product['name']}")

            # Get the base name without existing can size notation
            base_name = product['name']
            # Remove any existing (X oz can) notation
            base_name = re.sub(r'\s*\([^)]*oz\s+can\)', '', base_name)

            # Update the first product to be for the smallest size
            first_size = sizes[0]
            first_can_size = first_size['label']
            first_new_name = f"{base_name} ({first_can_size} can)"

            cursor.execute("""
                UPDATE products
                SET name = ?
                WHERE id = ?
            """, (first_new_name, product_id))

            cursor.execute("""
                UPDATE nutrition
                SET kcal_per_serving = ?,
                    serving_unit = ?
                WHERE product_id = ?
            """, (first_size['kcal'], f"{first_can_size} can", product_id))

            # Remove other sizes from sizes table for first product
            cursor.execute("""
                DELETE FROM sizes
                WHERE product_id = ? AND label != ?
            """, (product_id, first_can_size))

            print(f"  UPDATED original ({first_can_size})")

            # Create new products for remaining sizes
            for size in sizes[1:]:
                can_size = size['label']
                new_name = f"{base_name} ({can_size} can)"

                # Generate unique URL by appending size
                new_url = f"{product['url']}#{can_size.replace(' ', '')}"

                # Insert new product
                cursor.execute("""
                    INSERT INTO products (url, brand, name, type)
                    VALUES (?, ?, ?, ?)
                """, (new_url, product['brand'], new_name, product['type']))

                new_product_id = cursor.lastrowid

                # Insert nutrition for new product
                cursor.execute("""
                    INSERT INTO nutrition (
                        product_id, ga_basis, kcal_per_kg, kcal_per_serving,
                        serving_unit, protein_pct, fat_pct, fiber_pct,
                        moisture_pct, ash_pct, taurine_pct
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    new_product_id, product['ga_basis'], product['kcal_per_kg'],
                    size['kcal'], f"{can_size} can",
                    product['protein_pct'], product['fat_pct'], product['fiber_pct'],
                    product['moisture_pct'], product['ash_pct'], product['taurine_pct']
                ))

                # Insert size for new product
                cursor.execute("""
                    INSERT INTO sizes (product_id, label, grams, kcal)
                    VALUES (?, ?, ?, ?)
                """, (new_product_id, can_size, size['grams'], size['kcal']))

                created += 1
                print(f"  CREATED product {new_product_id} ({can_size})")

            processed += 1

    conn.commit()
    conn.close()

    print(f"\nDone!")
    print(f"Processed: {processed} products")
    print(f"Created:   {created} new product entries")

if __name__ == "__main__":
    main()
