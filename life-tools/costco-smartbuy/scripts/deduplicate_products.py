#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database & Frontend Deduplication Script
Unifies legacy prefixed IDs (e.g. 'costco-115174') and pure SKUs ('115174')
into canonical unique products, merging attributes and eliminating duplicate cards.
"""

import os
import sys
import json
import sqlite3
import shutil
from datetime import datetime

# Windows encoding safety
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "costco_products.db")
BACKUP_PATH = os.path.join(PROJECT_ROOT, "costco_products.db.bak")
PUBLIC_JSON_PATH = os.path.join(PROJECT_ROOT, "public", "data", "products.json")
SRC_JSON_PATH = os.path.join(PROJECT_ROOT, "src", "data", "products.json")

def merge_duplicate_rows(rows):
    # Sort rows so that pure numeric id comes first if available
    rows.sort(key=lambda r: (
        0 if not str(r['id']).startswith('costco-') and not '-' in str(r['id']) else 1,
        0 if r.get('is_estimated_price', 1) == 0 and (r.get('original_price') or 0) > 0 else 1
    ))
    
    primary = dict(rows[0])
    sku = primary.get('costco_item_number') or str(primary['id']).replace('costco-', '')
    primary['id'] = sku
    primary['costco_item_number'] = sku

    for other in rows[1:]:
        # Merge non-null / better fields
        for field in [
            'original_price', 'discount_amount', 'discount_end_date', 'package_spec',
            'total_weight_grams', 'storage_type', 'note', 'image_url', 'local_image_path',
            'pricing_type', 'price_per_kg', 'price_source', 'verified_source',
            'historical_range_min', 'historical_range_max', 'is_estimated_price', 'price_origin'
        ]:
            val = other.get(field)
            curr = primary.get(field)
            
            if field == 'original_price':
                if (not curr or curr == 0) and val and val > 0:
                    primary['original_price'] = val
            elif field == 'discount_amount':
                if (not curr or curr == 0) and val and val > 0:
                    primary['discount_amount'] = val
                    primary['discount_end_date'] = other.get('discount_end_date')
            elif field in ['note', 'local_image_path', 'verified_source', 'historical_range_min', 'historical_range_max', 'price_per_kg']:
                if not curr and val:
                    primary[field] = val
            elif field == 'pricing_type':
                if curr != 'by_weight' and val == 'by_weight':
                    primary['pricing_type'] = 'by_weight'
            elif field == 'is_estimated_price':
                if curr == 1 and val == 0:
                    primary['is_estimated_price'] = 0
                    primary['price_origin'] = other.get('price_origin')
                    
    return primary

def main():
    print(f"[*] Starting Costco Product Database Deduplication...")
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] Database not found at {DB_PATH}")
        return 1

    # 1. Backup DB
    shutil.copyfile(DB_PATH, BACKUP_PATH)
    print(f"[+] Created database backup at {BACKUP_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM products ORDER BY id")
    all_rows = [dict(r) for r in c.fetchall()]
    total_original = len(all_rows)
    print(f"[*] Loaded {total_original} rows from SQLite database.")

    # 2. Group by canonical SKU
    grouped = {}
    for d in all_rows:
        sku = d.get('costco_item_number')
        row_id = str(d.get('id', ''))
        
        if sku and sku.strip():
            canonical_key = sku.strip()
        elif row_id.startswith('costco-'):
            canonical_key = row_id.replace('costco-', '').strip()
        else:
            canonical_key = row_id.strip()
            
        if canonical_key not in grouped:
            grouped[canonical_key] = []
        grouped[canonical_key].append(d)

    print(f"[*] Deduplicated into {len(grouped)} canonical unique products.")
    duplicate_groups = sum(1 for v in grouped.values() if len(v) > 1)
    print(f"[*] Resolved {duplicate_groups} duplicate product groups.")

    # 3. Merge attributes
    merged_products = []
    for canonical_key, rows in grouped.items():
        if len(rows) == 1:
            prod = dict(rows[0])
            # Normalize id to canonical_key (SKU)
            if canonical_key and canonical_key != str(prod['id']):
                prod['id'] = canonical_key
                prod['costco_item_number'] = canonical_key
            merged_products.append(prod)
        else:
            merged = merge_duplicate_rows(rows)
            merged_products.append(merged)

    # 4. Rewrite SQLite database table
    print(f"[*] Rewriting products table in SQLite...")
    c.execute("DELETE FROM products")

    insert_sql = """
    INSERT INTO products (
        id, name, category, sub_category, original_price, discount_amount,
        discount_end_date, package_spec, total_weight_grams, unit_type,
        tag_type, historical_benchmark, storage_type, note, image_url,
        local_image_path, pricing_type, price_per_kg, price_source,
        costco_item_number, verified_source, historical_range_min, historical_range_max,
        is_estimated_price, price_origin, updated_at
    ) VALUES (
        :id, :name, :category, :sub_category, :original_price, :discount_amount,
        :discount_end_date, :package_spec, :total_weight_grams, :unit_type,
        :tag_type, :historical_benchmark, :storage_type, :note, :image_url,
        :local_image_path, :pricing_type, :price_per_kg, :price_source,
        :costco_item_number, :verified_source, :historical_range_min, :historical_range_max,
        :is_estimated_price, :price_origin, CURRENT_TIMESTAMP
    )
    """

    for p in merged_products:
        c.execute(insert_sql, p)

    conn.commit()
    print(f"[+] SQLite database successfully updated with {len(merged_products)} unique products.")

    # 5. Export to frontend JSON
    c.execute("""
        SELECT 
            id, name, category, sub_category, original_price, discount_amount,
            discount_end_date, package_spec, total_weight_grams, unit_type,
            tag_type, historical_benchmark, storage_type, note, image_url,
            local_image_path, pricing_type, price_per_kg, price_source,
            costco_item_number, verified_source, is_estimated_price, price_origin,
            historical_range_min, historical_range_max
        FROM products
        ORDER BY id
    """)

    all_db_rows = c.fetchall()
    conn.close()

    frontend_list = []
    for r in all_db_rows:
        hist_range = None
        if r[23] is not None and r[24] is not None:
            hist_range = [r[23], r[24]]

        item = {
            "id": r[0],
            "name": r[1],
            "category": r[2],
            "subCategory": r[3] or "",
            "originalPrice": r[4],
            "discountAmount": r[5] or 0,
            "discountEndDate": r[6],
            "packageSpec": r[7],
            "totalWeightInGrams": r[8],
            "unitType": r[9] or "g",
            "tagType": r[10] or "none",
            "historicalBenchmark": r[11] or "standard",
            "storageType": r[12] or "cold",
            "note": r[13] or "",
            "imageUrl": r[14] or "",
            "localImage": r[15],
            "pricingType": r[16] or "fixed_package",
            "pricePerKg": r[17],
            "priceSource": r[18] or "online",
            "costcoItemNumber": r[19] or r[0],
            "verifiedSource": r[20],
            "isEstimatedPrice": bool(r[21]),
            "priceOrigin": r[22] or "online",
            "historicalRange": hist_range
        }
        frontend_list.append(item)

    print(f"[*] Exporting {len(frontend_list)} unique products to frontend JSON...")
    for target in [PUBLIC_JSON_PATH, SRC_JSON_PATH]:
        with open(target, 'w', encoding='utf-8') as f:
            json.dump(frontend_list, f, ensure_ascii=False, indent=2)
        print(f"  [SAVED] {target}")

    print(f"\n[SUCCESS] Deduplication finished!")
    print(f"  - Original rows: {total_original}")
    print(f"  - Duplicate groups resolved: {duplicate_groups}")
    print(f"  - Clean unique products: {len(frontend_list)}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
