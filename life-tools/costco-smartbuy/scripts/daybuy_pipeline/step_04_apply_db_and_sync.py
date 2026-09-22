#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 04: Apply Verified Prices and Photos to SQLite Database and Frontend Assets
Strictly compliant with AGENTS.md

Accepts:
  --input: Path to verified_products_update.json from Step 03
  --db: Path to costco_products.db
  --public-json: Target public/data/products.json
  --src-json: Target src/data/products.json
  --force: Force synchronization
"""

import os
import sys
import json
import sqlite3
import argparse
from datetime import datetime, timezone

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def parse_args():
    parser = argparse.ArgumentParser(description="Step 04: Apply verified prices to DB and frontend")
    parser.add_argument("--input", required=True, help="Input verified updates JSON")
    parser.add_argument("--db", default="costco_products.db", help="Path to SQLite database")
    parser.add_argument("--public-json", default="public/data/products.json", help="Path to public products.json")
    parser.add_argument("--src-json", default="src/data/products.json", help="Path to src products.json")
    parser.add_argument("--force", action="store_true", help="Force sync")
    return parser.parse_args()

def main():
    args = parse_args()
    input_path = os.path.abspath(args.input)
    db_path = os.path.abspath(args.db)
    public_json = os.path.abspath(args.public_json)
    src_json = os.path.abspath(args.src_json)

    if not os.path.exists(input_path):
        print(f"[ERROR] Input file not found: {input_path}")
        return 1

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    updates = data.get("verified_updates", [])
    print(f"[*] Connecting to SQLite database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    now_iso = datetime.now(timezone.utc).isoformat()
    applied_count = 0

    for u in updates:
        pid = u["productId"]
        price = u["verifiedPrice"]
        v_source = u["verifiedSource"]
        local_img = u.get("localImagePath")
        remote_img = u.get("remoteImageUrl")
        hist_min = u.get("historicalMin")
        hist_max = u.get("historicalMax")

        # Convert historical total price to 100g range if product weight is available
        cursor.execute("SELECT total_weight_grams, name FROM products WHERE id = ?", (pid,))
        p_row = cursor.fetchone()
        weight = p_row[0] if p_row and p_row[0] else 1000

        min_per_100g = round((hist_min / weight) * 100, 1) if weight and hist_min else None
        max_per_100g = round((hist_max / weight) * 100, 1) if weight and hist_max else None

        cursor.execute("""
            UPDATE products
            SET original_price = ?,
                is_estimated_price = 0,
                price_origin = 'store_tag',
                verified_source = ?,
                price_source = 'warehouse_only',
                local_image_path = COALESCE(?, local_image_path),
                image_url = COALESCE(?, image_url),
                historical_range_min = ?,
                historical_range_max = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            price, v_source, local_img, remote_img,
            min_per_100g, max_per_100g, now_iso, pid
        ))
        applied_count += 1

    conn.commit()
    print(f"[SUCCESS] Applied verified prices and photos to {applied_count} products in database.")

    # Check remaining guessed/zero price products
    cursor.execute("SELECT COUNT(*) FROM products WHERE original_price = 0 OR is_estimated_price = 1")
    remaining_count = cursor.fetchone()[0]
    print(f"[STATUS] Remaining products with estimated/zero prices: {remaining_count}")

    # Export all products from DB
    cursor.execute("""
    SELECT id, name, category, sub_category, original_price, discount_amount,
           discount_end_date, package_spec, total_weight_grams, unit_type,
           tag_type, historical_benchmark, storage_type, note, image_url,
           local_image_path, pricing_type, price_per_kg, price_source,
           costco_item_number, verified_source, is_estimated_price, price_origin,
           historical_range_min, historical_range_max
    FROM products
    ORDER BY (original_price > 0) DESC, category, name;
    """)

    all_exported = []
    for r in cursor.fetchall():
        item = {
            "id": r[0],
            "name": r[1],
            "category": r[2],
            "subCategory": r[3],
            "originalPrice": float(r[4]),
            "discountAmount": float(r[5]) if r[5] else 0,
            "discountEndDate": r[6],
            "packageSpec": r[7] or "標準規格",
            "totalWeightInGrams": int(r[8]),
            "unitType": r[9] or "g",
            "tagType": r[10] or "none",
            "historicalBenchmark": r[11] or "standard",
            "storageType": r[12] or "room",
            "note": r[13],
            "imageUrl": r[14],
            "localImage": r[15],
            "pricingType": r[16] or "fixed_package",
            "pricePerKg": float(r[17]) if r[17] else None,
            "priceSource": r[18] or "online_catalog",
            "costcoItemNumber": r[19],
            "verifiedSource": r[20],
            "isEstimatedPrice": bool(r[21]),
            "priceOrigin": r[22] or "flyer_official"
        }
        if r[23] is not None and r[24] is not None:
            item["historicalRange"] = {
                "minPer100g": float(r[23]),
                "maxPer100g": float(r[24])
            }
        all_exported.append(item)

    conn.close()

    os.makedirs(os.path.dirname(public_json), exist_ok=True)
    os.makedirs(os.path.dirname(src_json), exist_ok=True)

    with open(public_json, "w", encoding="utf-8") as f:
        json.dump(all_exported, f, ensure_ascii=False, indent=2)

    with open(src_json, "w", encoding="utf-8") as f:
        json.dump(all_exported, f, ensure_ascii=False, indent=2)

    print(f"\n[EXPORT] Total synchronized products: {len(all_exported)}")
    print(f"[EXPORT] Synchronized to {public_json} and {src_json}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
