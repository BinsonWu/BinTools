#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 04: Synchronize Active Deals to SQLite Database and Frontend UI
Strictly compliant with AGENTS.md

Accepts:
  --input: Path to enriched_deals.json from Step 03
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
    parser = argparse.ArgumentParser(description="Step 04: Sync deals to DB and frontend")
    parser.add_argument("--input", required=True, help="Input enriched deals JSON")
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

    active_deals = data.get("active_deals", [])
    active_deal_ids = set(str(d["id"]) for d in active_deals)
    active_deals_map = {str(d["id"]): d for d in active_deals}

    print(f"[*] Connecting to SQLite database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    now_iso = datetime.now(timezone.utc).isoformat()

    # 1. Reset expired/obsolete discounts for online catalog items
    cursor.execute("SELECT id, name, discount_amount FROM products WHERE discount_amount > 0 AND price_source = 'online_catalog'")
    currently_discounted = cursor.fetchall()
    reset_count = 0
    for row in currently_discounted:
        pid = str(row[0])
        if pid not in active_deal_ids:
            cursor.execute("""
                UPDATE products 
                SET discount_amount = 0, discount_end_date = NULL, tag_type = 'none', updated_at = ?
                WHERE id = ?
            """, (now_iso, pid))
            reset_count += 1

    print(f"[RESET] Cleared expired discounts on {reset_count} products.")

    # 2. Update active deals on existing items, or insert new deal items
    updated_deals_count = 0
    inserted_deals_count = 0

    for deal in active_deals:
        pid = str(deal["id"])
        disc_amt = deal["discountAmount"]
        disc_end = deal["discountEndDate"]
        tag_type = deal["tagType"]

        cursor.execute("SELECT id, original_price FROM products WHERE id = ?", (pid,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE products
                SET discount_amount = ?, discount_end_date = ?, tag_type = ?, updated_at = ?
                WHERE id = ?
            """, (disc_amt, disc_end, tag_type, now_iso, pid))
            updated_deals_count += 1
        else:
            # Insert newly discovered deal item into database
            name = deal["name"]
            orig_price = deal["originalPrice"]
            spec = deal.get("packageSpec", "標準規格")
            weight = deal.get("totalWeightInGrams", 1000)
            unit = deal.get("unitType", "g")
            img_url = deal.get("imageUrl")
            costco_no = deal.get("costcoItemNumber", pid)

            cursor.execute("""
                INSERT INTO products (
                    id, name, category, sub_category, original_price, discount_amount,
                    discount_end_date, package_spec, total_weight_grams, unit_type,
                    tag_type, historical_benchmark, storage_type, note, image_url,
                    pricing_type, price_source, costco_item_number, verified_source,
                    is_estimated_price, price_origin, updated_at
                ) VALUES (
                    ?, ?, 'pantry', '本週特價專區', ?, ?,
                    ?, ?, ?, ?,
                    ?, 'historical_low', 'room', '官方即時特惠商品', ?,
                    'fixed_package', 'online_catalog', ?, '好市多最新特價目錄',
                    0, 'flyer_official', ?
                )
            """, (
                pid, name, orig_price, disc_amt,
                disc_end, spec, weight, unit,
                tag_type, img_url, costco_no, now_iso
            ))
            inserted_deals_count += 1

    conn.commit()
    print(f"[SUCCESS] Updated {updated_deals_count} existing items with active deals.")
    print(f"[SUCCESS] Added {inserted_deals_count} new promotional deal items into DB.")

    # 3. Export all products from DB
    cursor.execute("""
    SELECT id, name, category, sub_category, original_price, discount_amount,
           discount_end_date, package_spec, total_weight_grams, unit_type,
           tag_type, historical_benchmark, storage_type, note, image_url,
           local_image_path, pricing_type, price_per_kg, price_source,
           costco_item_number, verified_source, is_estimated_price, price_origin,
           historical_range_min, historical_range_max
    FROM products
    ORDER BY (discount_amount > 0) DESC, discount_amount DESC, name;
    """)

    all_exported = []
    discounted_total = 0

    for r in cursor.fetchall():
        disc_amt = float(r[5]) if r[5] else 0
        if disc_amt > 0:
            discounted_total += 1

        item = {
            "id": r[0],
            "name": r[1],
            "category": r[2],
            "subCategory": r[3],
            "originalPrice": float(r[4]),
            "discountAmount": disc_amt,
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

    print(f"\n[EXPORT] Total products in database: {len(all_exported)}")
    print(f"[EXPORT] Total products with active discounts: {discounted_total}")
    print(f"[EXPORT] Synchronized to {public_json} and {src_json}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
