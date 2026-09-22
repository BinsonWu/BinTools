#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 04: Sync Processed Products to SQLite DB and Frontend JSON Assets
Accepts:
  --input: Path to c8_processed_products.json from Step 03
  --db: Path to costco_products.db
  --public-json: Target public/data/products.json
  --src-json: Target src/data/products.json
  --force: Force sync even if target files exist
"""

import os
import sys
import json
import sqlite3
import argparse
from datetime import datetime

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def parse_args():
    parser = argparse.ArgumentParser(description="Step 04: Sync DB and frontend assets")
    parser.add_argument("--input", required=True, help="Input processed products JSON")
    parser.add_argument("--db", default="costco_products.db", help="Path to SQLite database")
    parser.add_argument("--public-json", default="public/data/products.json", help="Path to public products.json")
    parser.add_argument("--src-json", default="src/data/products.json", help="Path to src products.json")
    parser.add_argument("--force", action="store_true", help="Force sync")
    return parser.parse_args()

def init_db(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        sub_category TEXT,
        original_price REAL NOT NULL,
        discount_amount REAL DEFAULT 0,
        discount_end_date TEXT,
        package_spec TEXT,
        total_weight_grams INTEGER NOT NULL,
        unit_type TEXT DEFAULT 'g',
        tag_type TEXT DEFAULT 'none',
        historical_benchmark TEXT DEFAULT 'standard',
        storage_type TEXT DEFAULT 'room',
        note TEXT,
        image_url TEXT,
        local_image_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        pricing_type TEXT DEFAULT 'fixed_package',
        price_per_kg REAL,
        price_source TEXT DEFAULT 'online_catalog',
        costco_item_number TEXT,
        verified_source TEXT DEFAULT '好市多線上購物官方目錄',
        historical_range_min REAL,
        historical_range_max REAL,
        is_estimated_price INTEGER DEFAULT 0,
        price_origin TEXT DEFAULT 'flyer_official'
    );
    """)

def main():
    args = parse_args()
    input_path = os.path.abspath(args.input)
    db_path = os.path.abspath(args.db)
    public_json_path = os.path.abspath(args.public_json)
    src_json_path = os.path.abspath(args.src_json)

    if not os.path.exists(input_path):
        print(f"[ERROR] Input file not found: {input_path}")
        return 1

    with open(input_path, "r", encoding="utf-8") as f:
        products = json.load(f)

    print(f"[*] Connecting to SQLite database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    init_db(cursor)

    upsert_count = 0
    now_iso = datetime.utcnow().isoformat()

    for p in products:
        pid = p["id"]
        name = p["name"]
        cat = p["category"]
        subcat = p.get("subCategory")
        orig_price = p.get("originalPrice", 0)
        disc_amt = p.get("discountAmount", 0)
        disc_end = p.get("discountEndDate")
        spec = p.get("packageSpec", "")
        weight = p.get("totalWeightInGrams", 1000)
        unit = p.get("unitType", "g")
        tag = p.get("tagType", "none")
        benchmark = p.get("historicalBenchmark", "standard")
        storage = p.get("storageType", "room")
        note = p.get("note")
        img_url = p.get("imageUrl")
        local_img = p.get("localImage")
        pricing_type = p.get("pricingType", "fixed_package")
        price_per_kg = p.get("pricePerKg")
        price_source = p.get("priceSource", "online_catalog")
        item_no = p.get("costcoItemNumber", pid)
        verified_source = p.get("verifiedSource", "好市多官方商品目錄")
        is_est = 1 if p.get("isEstimatedPrice") else 0
        price_origin = p.get("priceOrigin", "flyer_official")

        cursor.execute("""
        INSERT INTO products (
            id, name, category, sub_category, original_price, discount_amount,
            discount_end_date, package_spec, total_weight_grams, unit_type,
            tag_type, historical_benchmark, storage_type, note, image_url,
            local_image_path, pricing_type, price_per_kg, price_source,
            costco_item_number, verified_source, is_estimated_price, price_origin,
            updated_at
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            category=excluded.category,
            sub_category=excluded.sub_category,
            original_price=excluded.original_price,
            discount_amount=excluded.discount_amount,
            discount_end_date=excluded.discount_end_date,
            package_spec=excluded.package_spec,
            total_weight_grams=excluded.total_weight_grams,
            unit_type=excluded.unit_type,
            tag_type=excluded.tag_type,
            storage_type=excluded.storage_type,
            image_url=excluded.image_url,
            local_image_path=COALESCE(excluded.local_image_path, products.local_image_path),
            pricing_type=excluded.pricing_type,
            price_source=excluded.price_source,
            verified_source=excluded.verified_source,
            is_estimated_price=excluded.is_estimated_price,
            price_origin=excluded.price_origin,
            updated_at=excluded.updated_at;
        """, (
            pid, name, cat, subcat, orig_price, disc_amt,
            disc_end, spec, weight, unit,
            tag, benchmark, storage, note, img_url,
            local_img, pricing_type, price_per_kg, price_source,
            item_no, verified_source, is_est, price_origin,
            now_iso
        ))
        upsert_count += 1

    conn.commit()
    print(f"[SUCCESS] Upserted {upsert_count} products into SQLite products table.")

    # Export all products from DB to ensure complete sync
    cursor.execute("""
    SELECT id, name, category, sub_category, original_price, discount_amount,
           discount_end_date, package_spec, total_weight_grams, unit_type,
           tag_type, historical_benchmark, storage_type, note, image_url,
           local_image_path, pricing_type, price_per_kg, price_source,
           costco_item_number, verified_source, is_estimated_price, price_origin,
           historical_range_min, historical_range_max
    FROM products
    ORDER BY category, name;
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

    # Save to public and src
    os.makedirs(os.path.dirname(public_json_path), exist_ok=True)
    os.makedirs(os.path.dirname(src_json_path), exist_ok=True)

    with open(public_json_path, "w", encoding="utf-8") as f:
        json.dump(all_exported, f, ensure_ascii=False, indent=2)

    with open(src_json_path, "w", encoding="utf-8") as f:
        json.dump(all_exported, f, ensure_ascii=False, indent=2)

    print(f"[EXPORT] Saved {len(all_exported)} products to {public_json_path}")
    print(f"[EXPORT] Saved {len(all_exported)} products to {src_json_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
