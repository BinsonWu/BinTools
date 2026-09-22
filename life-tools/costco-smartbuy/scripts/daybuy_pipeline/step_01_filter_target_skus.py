#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 01: Filter Target Products With Guessed or Zero Original Prices
Strictly compliant with AGENTS.md

Accepts:
  --output: Target JSON path for target SKUs manifest
  --db: Path to costco_products.db
  --force: Force overwrite existing output
"""

import os
import sys
import json
import sqlite3
import re
import argparse
from datetime import datetime, timezone

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def parse_args():
    parser = argparse.ArgumentParser(description="Step 01: Filter guessed/zero price products")
    parser.add_argument("--output", required=True, help="Target JSON output path for SKUs manifest")
    parser.add_argument("--db", default="costco_products.db", help="Path to SQLite database")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing output")
    return parser.parse_args()

def extract_clean_sku(item_no, pid, name):
    # Try costco_item_number first
    if item_no and item_no.isdigit():
        return item_no

    # Try product id if numeric
    if pid and pid.isdigit():
        return pid

    # Try finding digits in item_no or pid
    m = re.search(r'\b(\d{5,7})\b', str(item_no) + " " + str(pid))
    if m:
        return m.group(1)

    # Try finding digits in product title: e.g. #118583
    m_name = re.search(r'#?(\d{5,7})\b', name)
    if m_name:
        return m_name.group(1)

    return None

def main():
    args = parse_args()
    output_path = os.path.abspath(args.output)
    db_path = os.path.abspath(args.db)

    if not os.path.exists(db_path):
        print(f"[ERROR] Database not found: {db_path}")
        return 1

    if os.path.exists(output_path) and not args.force:
        print(f"[SKIP] Output already exists at {output_path}. Use --force to rerun.")
        return 0

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print(f"[*] Querying database at {db_path} for products with estimated or zero prices...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, name, category, sub_category, original_price, is_estimated_price,
           price_origin, verified_source, package_spec, total_weight_grams,
           unit_type, price_source, costco_item_number, image_url, local_image_path
    FROM products
    WHERE original_price = 0 OR is_estimated_price = 1 OR price_origin = 'calculated_by_weight'
    ORDER BY (original_price = 0) DESC, category, name;
    """)

    rows = cursor.fetchall()
    conn.close()

    target_items = []
    seen_skus = set()

    for r in rows:
        pid = r[0]
        name = r[1]
        cat = r[2]
        subcat = r[3]
        orig_price = float(r[4])
        is_est = bool(r[5])
        price_orig = r[6]
        verified = r[7]
        spec = r[8]
        weight = r[9]
        unit = r[10]
        price_src = r[11]
        item_no = r[12]
        img_url = r[13]
        local_img = r[14]

        sku = extract_clean_sku(item_no, pid, name)
        if not sku:
            continue

        target_items.append({
            "id": pid,
            "sku": sku,
            "name": name,
            "category": cat,
            "subCategory": subcat,
            "currentOriginalPrice": orig_price,
            "isEstimatedPrice": is_est,
            "priceOrigin": price_orig,
            "verifiedSource": verified,
            "packageSpec": spec,
            "totalWeightInGrams": weight,
            "unitType": unit,
            "priceSource": price_src,
            "imageUrl": img_url,
            "localImagePath": local_img
        })
        seen_skus.add(sku)

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_targets_count": len(target_items),
        "unique_skus_count": len(seen_skus),
        "target_items": target_items
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"[SUCCESS] Step 01 finished. Identified {len(target_items)} target items ({len(seen_skus)} unique SKUs).")
    print(f"[OUTPUT] Saved manifest to {output_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
