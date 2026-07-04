#!/usr/bin/env python3
"""
petfood.express cat-food scraper -> SQLite (slim version)

Pet Food Express runs on BigCommerce (Stencil). The category grid is JS-loaded,
but individual PRODUCT pages are server-rendered, so the Guaranteed Analysis and
calorie content are in the raw HTML and read with plain `requests`.

Pipeline:
  1. Pull product URLs from the XML sitemap (no JS required).
  2. Fetch each /products/{slug}.html page.
  3. Parse name, brand, GA, and calories from the static HTML.
  4. Classify wet/dry from moisture, then load into SQLite.

CALORIES: only PRINTED values are stored. If a page lists no kcal figure, the
kcal columns are left NULL (to be backfilled from another source later). No
estimation is performed.

GUARANTEED ANALYSIS: pages come in two layouts, both handled --
  * "guaranteed": Crude Protein (Min) 8.0% ...      (AAFCO min/max)
  * "typical":    Protein 12.24%  Fat 2.50% ...      (typical values, no min/max)
The ga_basis column records which one a row came from -- it matters, because
typical values are more accurate than guaranteed minimums.

BEFORE RUNNING: read https://www.petfood.express/robots.txt and their Terms of
Use. Keep REQUEST_DELAY polite; don't parallelize. Pages cache to disk so
re-runs and schema tweaks don't re-hit the site.

Dependencies:
    pip install requests beautifulsoup4 lxml
"""

import re
import json
import time
import sqlite3
import logging
import xml.etree.ElementTree as ET
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
BASE_URL      = "https://www.petfood.express"
SITEMAP_INDEX = f"{BASE_URL}/xmlsitemap.php"   # BigCommerce default; verify in robots.txt
DB_PATH       = "data/catfood.db"
CACHE_DIR     = Path("cache")
REQUEST_DELAY = 3.0
TIMEOUT       = 30
USER_AGENT    = "personal-catfood-research/1.0 (+mailto:you@example.com)"

# Canonical brand -> aliases that may appear at the START of a product name.
# The category facet label isn't always how a product is named: "Wellness Pet
# Company" ships products called just "Wellness ...", Tiki's cat line is "Tiki
# Cat", etc. Longest alias wins so "Tiki Cat" is matched before "Tiki".
BRAND_ALIASES = {
    "Acana": ["Acana"],
    "Applaws": ["Applaws"],
    "Bixbi": ["Bixbi"],
    "Blue Buffalo": ["Blue Buffalo"],
    "Canagan": ["Canagan"],
    "Caru Pet Food Company": ["Caru"],
    "Farmina Pet Foods": ["Farmina"],
    "FirstMate": ["FirstMate", "First Mate"],
    "Fromm Family Pet Food": ["Fromm"],
    "Fruitables": ["Fruitables"],
    "Fussie Cat": ["Fussie Cat", "Fussie"],
    "Hill's": ["Hill's", "Hills", "Science Diet"],
    "Instinct": ["Instinct"],
    "JustFoodForDogs": ["JustFoodForDogs", "Just Food For Dogs"],
    "Kiwi Kitchens": ["Kiwi Kitchens"],
    "Nulo": ["Nulo"],
    "NutriSource": ["NutriSource", "Nutri Source"],
    "Open Farm": ["Open Farm"],
    "Orijen": ["Orijen"],
    "Pet Food Express": ["Pet Food Express"],
    "PetAg": ["PetAg", "Pet-Ag"],
    "Portland Pet Food Company": ["Portland Pet Food"],
    "Primal": ["Primal"],
    "RAWZ Natural Pet Food": ["RAWZ", "Rawz"],
    "Safe Catch": ["Safe Catch"],
    "Smallbatch Pets": ["Smallbatch", "Small Batch"],
    "Smalls": ["Smalls"],
    "Stella & Chewy's": ["Stella & Chewy's", "Stella and Chewy's", "Stella & Chewy", "Stella"],
    "Taste of the Wild": ["Taste of the Wild"],
    "The Honest Kitchen": ["The Honest Kitchen", "Honest Kitchen"],
    "Tiki Pets": ["Tiki Cat", "Tiki Pets", "Tiki"],
    "Tucker's": ["Tucker's", "Tuckers"],
    "Vital Essentials": ["Vital Essentials"],
    "Wellness Pet Company": ["Wellness"],
    "Weruva": ["Weruva"],
    "ZIWI Peak": ["ZIWI Peak", "Ziwi Peak", "Ziwi"],
}
# Flatten to (alias_lower, canonical), longest alias first so the most specific
# match wins ("Tiki Cat" before "Tiki").
_ALIAS_INDEX = sorted(
    ((a.lower(), canon) for canon, al in BRAND_ALIASES.items() for a in al),
    key=lambda t: len(t[0]), reverse=True,
)

CAT_HINT = re.compile(r"cat", re.I)
WET_MOISTURE_THRESHOLD = 50.0  # moisture % above this => wet food

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("petfood")

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})
CACHE_DIR.mkdir(exist_ok=True)


# --------------------------------------------------------------------------- #
# Fetching (on-disk cache + polite delay)
# --------------------------------------------------------------------------- #
def fetch(url: str, is_xml: bool = False) -> str | None:
    cache_file = CACHE_DIR / (re.sub(r"[^A-Za-z0-9]+", "_", url)[-200:] + (".xml" if is_xml else ".html"))
    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8", errors="replace")
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


# --------------------------------------------------------------------------- #
# Step 1: discover product URLs from the sitemap
# --------------------------------------------------------------------------- #
def _local(tag: str) -> str:
    return tag.split("}", 1)[-1]

def discover_product_urls() -> list[str]:
    seen: set[str] = set()
    queue = [SITEMAP_INDEX]
    products: list[str] = []
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
    log.info("found %d product URLs", len(products))
    return products


# --------------------------------------------------------------------------- #
# Step 2 + 3: parse a product page
# --------------------------------------------------------------------------- #
# Two GA layouts. Try guaranteed (min/max) first; fall back to typical.
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

# A purchasable size label, e.g. "3 oz", "5.5 oz", "12 lb". Full-string match so
# it only catches option labels, not stray mentions in the description prose.
SIZE_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*(oz|lb)\s*$", re.I)
GRAMS_PER = {"oz": 28.3495, "lb": 453.592}


def _meta(soup, prop):
    tag = soup.find("meta", attrs={"property": prop}) or soup.find("meta", attrs={"name": prop})
    return tag["content"].strip() if tag and tag.get("content") else None


def _description_text(soup):
    node = soup.find(id="tab-description") or soup.find(attrs={"class": "productView-description"})
    return node.get_text("\n") if node else soup.get_text("\n")


def _brand_from_page(soup):
    """BigCommerce/Stencil usually embeds the brand in JSON-LD or a meta tag --
    that's authoritative, so prefer it over guessing from the name."""
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
    """Map a raw brand string to the canonical facet label when recognized."""
    b = brand.lower()
    for alias, canon in _ALIAS_INDEX:
        if b == alias or b.startswith(alias):
            return canon
    return brand


def resolve_brand(soup, name):
    # 1) authoritative brand printed on the page
    page_brand = _brand_from_page(soup)
    if page_brand:
        return _canonicalize(page_brand)
    # 2) match a known brand alias as a prefix of the product name
    nm = (name or "").lower()
    for alias, canon in _ALIAS_INDEX:
        if nm.startswith(alias):
            return canon
    # 3) fallback: first word of the name
    return name.split()[0] if name else None


def parse_sizes(soup):
    """A product page has ONE recipe but may sell several sizes (3 oz, 5.5 oz...).
    Sizes render as variant option labels in the static HTML. We read them from
    option-like elements only, and normalize each to grams for kcal math.

    NOTE: the exact option markup is the thing most likely to need tweaking --
    inspect one real page's HTML and adjust the selector if sizes come back empty.
    """
    found = {}  # (value, unit) -> (raw_label, grams)  -- dedupes repeats
    candidates = soup.select(
        "label, option, "
        "[class*=form-option], [class*=swatch], "
        "[data-product-attribute] *"
    )
    # also consider radio/option input values like value="5.5 oz"
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

    # ---- Guaranteed analysis: try min/max layout, else typical layout ----
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
        return None  # no usable nutrition on the page

    # ---- Calories: store PRINTED values only; NULL if absent (no estimation) ----
    kcal_per_kg = kcal_per_serving = serving_unit = None
    for val, desc in KCAL.findall(text):
        val = float(val.replace(",", ""))
        desc_clean = desc.strip()
        desc_lower = desc_clean.lower()

        if "kg" in desc_lower:
            kcal_per_kg = val
        else:
            # Clean serving description: remove "per"/"/" prefix first
            desc_clean = re.sub(r'^(per|/)\s+', '', desc_clean, flags=re.I)
            desc_lower_cleaned = desc_clean.lower()

            # Check if it's kcal per PLAIN weight unit (oz, g, lb) - no quantity prefix
            plain_weight_match = re.match(r'^(oz|ounces?|grams?|g|pounds?|lbs?)\s*$', desc_lower_cleaned, re.I)

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

    # ---- wet vs dry from moisture ----
    moisture = nutrients["moisture_pct"]
    food_type = ("wet" if moisture >= WET_MOISTURE_THRESHOLD else "dry") if moisture is not None else None

    # For dry food with plain weight units in serving, clear the serving info
    # Keep container units like "cup" for dry food
    if food_type == "dry" and serving_unit:
        # Check if serving_unit is a plain weight unit (oz, g, lb) without quantity
        if re.match(r'^(oz|ounces?|grams?|g|pounds?|lbs?)\s*$', serving_unit, re.I):
            kcal_per_serving = None
            serving_unit = None

    # ---- purchasable sizes; derive per-size kcal from kcal/kg when we have it ----
    sizes = parse_sizes(soup)
    for s in sizes:
        s["kcal"] = round(kcal_per_kg * s["grams"] / 1000.0, 1) if kcal_per_kg is not None else None

    return {
        "url": url, "name": name, "brand": resolve_brand(soup, name),
        "type": food_type, "ga_basis": ga_basis,
        "kcal_per_kg": kcal_per_kg, "kcal_per_serving": kcal_per_serving,
        "serving_unit": serving_unit, "sizes": sizes, **nutrients,
    }


# --------------------------------------------------------------------------- #
# SQLite: products (metadata) + nutrition, plus a dry-matter view
# --------------------------------------------------------------------------- #
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

-- One row per purchasable size on a product page. The recipe (nutrition) is
-- shared; only the package weight differs. kcal is derived from kcal_per_kg, so
-- it is NULL whenever the page didn't print a calorie figure (backfill later).
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


def init_db(conn):
    conn.executescript(SCHEMA)
    conn.commit()


def upsert(conn, p):
    cur = conn.execute(
        """INSERT INTO products (url, brand, name, type) VALUES (?,?,?,?)
           ON CONFLICT(url) DO UPDATE SET
               brand=excluded.brand, name=excluded.name, type=excluded.type
           RETURNING id""",
        (p["url"], p["brand"], p["name"], p["type"]),
    )
    pid = cur.fetchone()[0]
    conn.execute(
        """INSERT INTO nutrition
           (product_id, ga_basis, kcal_per_kg, kcal_per_serving, serving_unit,
            protein_pct, fat_pct, fiber_pct, moisture_pct, ash_pct, taurine_pct)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)
           ON CONFLICT(product_id) DO UPDATE SET
               ga_basis=excluded.ga_basis,
               kcal_per_kg=excluded.kcal_per_kg,
               kcal_per_serving=excluded.kcal_per_serving,
               serving_unit=excluded.serving_unit,
               protein_pct=excluded.protein_pct, fat_pct=excluded.fat_pct,
               fiber_pct=excluded.fiber_pct, moisture_pct=excluded.moisture_pct,
               ash_pct=excluded.ash_pct, taurine_pct=excluded.taurine_pct""",
        (pid, p["ga_basis"], p["kcal_per_kg"], p["kcal_per_serving"], p["serving_unit"],
         p["protein_pct"], p["fat_pct"], p["fiber_pct"], p["moisture_pct"],
         p["ash_pct"], p["taurine_pct"]),
    )

    # replace this product's sizes so re-runs don't accumulate stale rows
    conn.execute("DELETE FROM sizes WHERE product_id=?", (pid,))
    for s in p.get("sizes", []):
        conn.execute(
            "INSERT OR IGNORE INTO sizes (product_id, label, grams, kcal) VALUES (?,?,?,?)",
            (pid, s["label"], s["grams"], s["kcal"]),
        )
    conn.commit()


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main():
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    cat_urls = [u for u in discover_product_urls() if CAT_HINT.search(u)]
    log.info("scraping %d candidate cat-food pages", len(cat_urls))

    stored = no_kcal = 0
    for n, url in enumerate(cat_urls, 1):
        html = fetch(url)
        if not html:
            continue
        product = parse_product(html, url)
        if not product:
            continue
        if product["kcal_per_kg"] is None and product["kcal_per_serving"] is None:
            no_kcal += 1
        upsert(conn, product)
        stored += 1
        if n % 25 == 0:
            log.info("...%d/%d processed, %d stored", n, len(cat_urls), stored)

    log.info("done: %d products stored (%d have no printed kcal -> backfill later)", stored, no_kcal)
    conn.close()


if __name__ == "__main__":
    main()
