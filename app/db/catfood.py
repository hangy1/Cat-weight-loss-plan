"""
Database connection and queries for catfood.db
"""
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Any
from contextlib import contextmanager

DB_PATH = Path(__file__).parent.parent.parent / "data" / "catfood.db"


@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    try:
        yield conn
    finally:
        conn.close()


def search_foods(
    query: str = "",
    brand: Optional[str] = None,
    food_type: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Search cat foods by name, brand, or type

    Args:
        query: Search text for product name
        brand: Filter by brand
        food_type: Filter by type ('wet' or 'dry')
        limit: Maximum results to return

    Returns:
        List of products with nutrition data
    """
    with get_db() as conn:
        sql = """
            SELECT
                p.id,
                p.name,
                p.brand,
                p.type,
                p.url,
                n.protein_pct,
                n.fat_pct,
                n.fiber_pct,
                n.moisture_pct,
                n.ash_pct,
                n.taurine_pct,
                n.kcal_per_kg,
                n.kcal_per_serving,
                n.serving_unit,
                n.ga_basis
            FROM products p
            JOIN nutrition n ON p.id = n.product_id
            WHERE 1=1
        """

        params = []

        if query:
            sql += " AND p.name LIKE ?"
            params.append(f"%{query}%")

        if brand:
            sql += " AND p.brand LIKE ?"
            params.append(f"%{brand}%")

        if food_type:
            sql += " AND p.type = ?"
            params.append(food_type)

        # Only show products with calorie data
        sql += " AND (n.kcal_per_kg IS NOT NULL OR n.kcal_per_serving IS NOT NULL)"

        sql += " ORDER BY p.name LIMIT ?"
        params.append(limit)

        cursor = conn.execute(sql, params)
        results = [dict(row) for row in cursor.fetchall()]

        return results


def get_food_by_id(product_id: int) -> Optional[Dict[str, Any]]:
    """Get detailed food information by product ID"""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT
                p.id,
                p.name,
                p.brand,
                p.type,
                p.url,
                n.protein_pct,
                n.fat_pct,
                n.fiber_pct,
                n.moisture_pct,
                n.ash_pct,
                n.taurine_pct,
                n.kcal_per_kg,
                n.kcal_per_serving,
                n.serving_unit,
                n.ga_basis
            FROM products p
            JOIN nutrition n ON p.id = n.product_id
            WHERE p.id = ?
        """, (product_id,))

        row = cursor.fetchone()
        return dict(row) if row else None


def get_food_sizes(product_id: int) -> List[Dict[str, Any]]:
    """Get available sizes for a product"""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT label, grams, kcal
            FROM sizes
            WHERE product_id = ?
            ORDER BY grams
        """, (product_id,))

        return [dict(row) for row in cursor.fetchall()]


def get_brands() -> List[str]:
    """Get list of all brands"""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT DISTINCT brand
            FROM products
            WHERE brand IS NOT NULL
            ORDER BY brand
        """)

        return [row[0] for row in cursor.fetchall()]


def get_dry_matter_nutrition(product_id: int) -> Optional[Dict[str, Any]]:
    """Get dry matter nutrition percentages"""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT
                id,
                brand,
                name,
                type,
                moisture_pct,
                protein_dm,
                fat_dm,
                fiber_dm,
                kcal_per_kg,
                kcal_per_serving,
                serving_unit
            FROM nutrition_dm
            WHERE id = ?
        """, (product_id,))

        row = cursor.fetchone()
        return dict(row) if row else None
