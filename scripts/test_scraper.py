#!/usr/bin/env python3
"""
Test version of petfood scraper - tests ONE brand only
"""

import re
import json
import time
import sqlite3
import logging
from pathlib import Path

import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

# Config
BASE_URL = "https://www.petfood.express"
SITEMAP_INDEX = f"{BASE_URL}/xmlsitemap.php"
DB_PATH = "data/catfood_test.db"
CACHE_DIR = Path("cache")
REQUEST_DELAY = 3.0
TIMEOUT = 30
USER_AGENT = "personal-catfood-research/1.0"

# TEST: limit to this brand and max products
TEST_BRAND = "Wellness"  # Change this to test different brands
MAX_PRODUCTS = 5  # Only scrape first 5 products

BRAND_ALIASES = {
    "Wellness Pet Company": ["Wellness"],
    "Tiki Pets": ["Tiki Cat", "Tiki Pets", "Tiki"],
    "Weruva": ["Weruva"],
}

_ALIAS_INDEX = sorted(
    ((a.lower(), canon) for canon, al in BRAND_ALIASES.items() for a in al),
    key=lambda t: len(t[0]), reverse=True,
)

CAT_HINT = re.compile(r"cat", re.I)
WET_MOISTURE_THRESHOLD = 50.0

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("petfood_test")

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})
CACHE_DIR.mkdir(exist_ok=True)

GA_GUARANTEED = re.compile(
    r"(?:Crude\s+)?(Protein|Fat|Fiber|Moisture|Ash|Taurine)\s*"
    r"\((Min|Max)\.?\)\s*([\d.]+)\s*%",
    re.I,
)
GA_TYPICAL = re.compile(
    r"(?:Crude\s+)?(Protein|Fat|Fiber|Moisture|Ash|Taurine)\s+([\d.]+)\s*%",
    re.I,
)
NUTRIENT_COL = {
    "protein": "protein_pct", "fat": "fat_pct", "fiber": "fiber_pct",
    "moisture": "moisture_pct", "ash": "ash_pct", "taurine": "taurine_pct",
}
KCAL = re.compile(r"([\d,]+(?:\.\d+)?)\s*kcal\s*(?:ME\s*)?(?:/|per)\s*([^,;|\n]+)", re.I)
SERVING_UNIT = re.compile(r"\b(can|cup|pouch|tray|oz|g|kg)\b", re.I)
SIZE_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*(oz|lb)\s*$", re.I)
GRAMS_PER = {"oz": 28.3495, "lb": 453.592}


def fetch(url: str, is_xml: bool = False) -> str | None:
    cache_file = CACHE_DIR / (re.sub(r"[^A-Za-z0-9]+", "_", url)[-200:] + (".xml" if is_xml else ".html"))
    if cache_file.exists():
        log.info(f"  (cached)")
        return cache_file.read_text(encoding="utf-8", errors="replace")

    log.info(f"  Fetching {url[:80]}...")
    time.sleep(REQUEST_DELAY)
    try:
        resp = SESSION.get(url, timeout=TIMEOUT)
    except requests.RequestException as e:
        log.warning("request failed %s: %s", url, e)
        return None
    if resp.status_code != 200:
        log.warning("HTTP %s for %s", resp.status_code, url)
        return None
    cache_file.write_text(resp.text, encoding="utf-8", errors="replace")
    return resp.text


def _local(tag: str) -> str:
    return tag.split("}", 1)[-1]


def discover_product_urls() -> list[str]:
    seen: set[str] = set()
    queue = [SITEMAP_INDEX]
    products: list[str] = []

    log.info("Discovering product URLs from sitemap...")
    while queue:
        xml = fetch(queue.pop(), is_xml=True)
        if not xml:
            continue
        try:
            root = ET.fromstring(xml)
        except ET.ParseError as e:
            log.warning("bad sitemap xml: %s", e)
            continue
        for loc in root.iter():
            if _local(loc.tag) != "loc" or not loc.text:
                continue
            u = loc.text.strip()
            if u in seen:
                continue
            seen.add(u)
            # Check if it's a sitemap URL (either ends with .xml or contains xmlsitemap.php)
            if u.endswith(".xml") or "xmlsitemap.php" in u:
                queue.append(u)
            elif "/products/" in u and u.endswith(".html"):
                products.append(u)

    log.info(f"Found {len(products)} total product URLs")
    return products


def _meta(soup, prop):
    tag = soup.find("meta", attrs={"property": prop}) or soup.find("meta", attrs={"name": prop})
    return tag["content"].strip() if tag and tag.get("content") else None


def _description_text(soup):
    node = soup.find(id="tab-description") or soup.find(attrs={"class": "productView-description"})
    return node.get_text("\n") if node else soup.get_text("\n")


def _brand_from_page(soup):
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
        except (ValueError, TypeError):
            continue
        for item in (data if isinstance(data, list) else [data]):
            b = item.get("brand") if isinstance(item, dict) else None
            if isinstance(b, dict):
                b = b.get("name")
            if isinstance(b, str) and b.strip():
                return b.strip()
    m = soup.find("meta", attrs={"property": "product:brand"}) or soup.find(attrs={"itemprop": "brand"})
    if m:
        val = m.get("content") or m.get_text(strip=True)
        if val:
            return val.strip()
    return None


def _canonicalize(brand):
    b = brand.lower()
    for alias, canon in _ALIAS_INDEX:
        if b == alias or b.startswith(alias):
            return canon
    return brand


def resolve_brand(soup, name):
    page_brand = _brand_from_page(soup)
    if page_brand:
        return _canonicalize(page_brand)
    nm = (name or "").lower()
    for alias, canon in _ALIAS_INDEX:
        if nm.startswith(alias):
            return canon
    return name.split()[0] if name else None


def parse_sizes(soup):
    found = {}
    candidates = soup.select(
        "label, option, "
        "[class*=form-option], [class*=swatch], "
        "[data-product-attribute] *"
    )
    for inp in soup.select("input[type=radio], input[type=hidden]"):
        if inp.get("value"):
            candidates.append(BeautifulSoup(f"<x>{inp['value']}</x>", "lxml").x)

    for el in candidates:
        if el is None:
            continue
        m = SIZE_RE.match(el.get_text(" ", strip=True))
        if not m:
            continue
        value, unit = float(m.group(1)), m.group(2).lower()
        grams = round(value * GRAMS_PER[unit], 1)
        found[(value, unit)] = (f"{m.group(1)} {unit}", grams)

    return [{"label": lbl, "grams": g} for (lbl, g) in found.values()]


def parse_product(html, url):
    soup = BeautifulSoup(html, "lxml")
    name = _meta(soup, "og:title") or (soup.find("h1").get_text(strip=True) if soup.find("h1") else None)
    if not name:
        return None
    text = _description_text(soup)

    nutrients = {c: None for c in NUTRIENT_COL.values()}
    ga_basis = None

    guaranteed = GA_GUARANTEED.findall(text)
    if guaranteed:
        ga_basis = "guaranteed"
        for nutrient, _basis, val in guaranteed:
            col = NUTRIENT_COL.get(nutrient.lower())
            if col:
                nutrients[col] = float(val)
    else:
        typical = GA_TYPICAL.findall(text)
        if typical:
            ga_basis = "typical"
            for nutrient, val in typical:
                col = NUTRIENT_COL.get(nutrient.lower())
                if col:
                    nutrients[col] = float(val)

    if all(v is None for v in nutrients.values()):
        return None

    kcal_per_kg = kcal_per_serving = serving_unit = None
    for val, desc in KCAL.findall(text):
        val = float(val.replace(",", ""))
        desc_clean = desc.strip()
        desc_lower = desc_clean.lower()

        if "kg" in desc_lower:
            kcal_per_kg = val
        else:
            # Clean serving description: remove "per"/"/" prefix
            desc_clean = re.sub(r'^(per|/)\s+', '', desc_clean, flags=re.I)

            # Check if it's kcal per PLAIN weight unit (oz, g, lb) - no quantity prefix
            plain_weight_match = re.match(r'^(oz|ounces?|grams?|g|pounds?|lbs?)\s*$', desc_clean, re.I)

            if plain_weight_match:
                # It's a plain weight unit like "32 kcal/oz"
                unit = plain_weight_match.group(1).lower()

                # Convert to kcal_per_kg
                if unit in ("oz", "ounce", "ounces"):
                    kcal_per_kg = round(val / GRAMS_PER["oz"] * 1000, 2)
                elif unit in ("g", "gram", "grams"):
                    kcal_per_kg = round(val * 1000, 2)
                elif unit in ("lb", "lbs", "pound", "pounds"):
                    kcal_per_kg = round(val / GRAMS_PER["lb"] * 1000, 2)

                # For wet food, also keep as serving
                # For dry food, don't keep plain weight as serving (will be cleared later)
                if kcal_per_serving is None:
                    kcal_per_serving = val
                    serving_unit = desc_clean
            else:
                # It's a serving description (e.g., "3 oz can", "cup", "8 oz cup")
                # Keep as serving for both wet and dry
                if kcal_per_serving is None:
                    kcal_per_serving = val
                    # Extract pattern: optional number + unit + optional container
                    match = re.match(r'(\d+(?:\.\d+)?\s+)?(\w+(?:\s+\w+)?)', desc_clean)
                    serving_unit = match.group(0).strip() if match else desc_clean[:30]

    moisture = nutrients["moisture_pct"]
    food_type = ("wet" if moisture >= WET_MOISTURE_THRESHOLD else "dry") if moisture is not None else None

    # For dry food with plain weight units in serving, clear the serving info
    # Keep container units like "cup" for dry food
    if food_type == "dry" and serving_unit:
        # Check if serving_unit is a plain weight unit (oz, g, lb) without quantity
        if re.match(r'^(oz|ounces?|grams?|g|pounds?|lbs?)\s*$', serving_unit, re.I):
            kcal_per_serving = None
            serving_unit = None

    sizes = parse_sizes(soup)
    for s in sizes:
        s["kcal"] = round(kcal_per_kg * s["grams"] / 1000.0, 1) if kcal_per_kg is not None else None

    return {
        "url": url, "name": name, "brand": resolve_brand(soup, name),
        "type": food_type, "ga_basis": ga_basis,
        "kcal_per_kg": kcal_per_kg, "kcal_per_serving": kcal_per_serving,
        "serving_unit": serving_unit, "sizes": sizes, **nutrients,
    }


def main():
    log.info(f"Testing scraper with brand: {TEST_BRAND}, max products: {MAX_PRODUCTS}")

    # Discover all cat product URLs
    all_urls = [u for u in discover_product_urls() if CAT_HINT.search(u)]
    log.info(f"Found {len(all_urls)} cat product URLs")

    # Filter to test brand
    brand_urls = []
    for url in all_urls:
        if TEST_BRAND.lower() in url.lower():
            brand_urls.append(url)
            if len(brand_urls) >= MAX_PRODUCTS:
                break

    log.info(f"Found {len(brand_urls)} {TEST_BRAND} URLs (testing first {MAX_PRODUCTS})")

    if not brand_urls:
        log.error(f"No URLs found for brand '{TEST_BRAND}'. Check if brand name is correct.")
        return

    # Process each product
    products = []
    for n, url in enumerate(brand_urls[:MAX_PRODUCTS], 1):
        log.info(f"\n--- Product {n}/{len(brand_urls[:MAX_PRODUCTS])} ---")
        log.info(f"URL: {url}")

        html = fetch(url)
        if not html:
            log.warning("  Failed to fetch")
            continue

        product = parse_product(html, url)
        if not product:
            log.warning("  Failed to parse (no nutrition data found)")
            continue

        products.append(product)

        # Print extracted data
        print(f"\n{'='*80}")
        print(f"Product: {product['name']}")
        print(f"Brand: {product['brand']}")
        print(f"Type: {product['type']}")
        print(f"GA Basis: {product['ga_basis']}")
        print(f"\nNutrition (as-fed %):")
        print(f"  Protein: {product['protein_pct']}")
        print(f"  Fat: {product['fat_pct']}")
        print(f"  Fiber: {product['fiber_pct']}")
        print(f"  Moisture: {product['moisture_pct']}")
        print(f"  Ash: {product['ash_pct']}")
        print(f"  Taurine: {product['taurine_pct']}")
        print(f"\nCalories:")
        print(f"  kcal/kg: {product['kcal_per_kg']}")
        print(f"  kcal/serving: {product['kcal_per_serving']} ({product['serving_unit']})")
        print(f"\nSizes: {product['sizes']}")
        print(f"{'='*80}\n")

    log.info(f"\n\nSUMMARY: Successfully parsed {len(products)}/{MAX_PRODUCTS} products")

    if products:
        log.info("\nSample data looks good! The scraper is working correctly.")
        log.info(f"To run full scrape, use: python petfood_scraper.py")


if __name__ == "__main__":
    main()
