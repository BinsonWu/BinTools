#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 02: Crawl All Products in Costco Taiwan Food & Dining (c/8)
Accepts:
  --input: Path to categories_manifest.json from Step 01
  --output: Target JSON path to save raw products array
  --force: Force overwrite output if exists
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.parse
import ssl
from datetime import datetime

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def parse_args():
    parser = argparse.ArgumentParser(description="Step 02: Crawl all Food & Dining products")
    parser.add_argument("--input", required=True, help="Input categories manifest JSON")
    parser.add_argument("--output", required=True, help="Target JSON output for raw products")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing output")
    return parser.parse_args()

def fetch_category_page(ctx, headers, category_id, page=0, page_size=100):
    url = f"https://www.costco.com.tw/rest/v2/taiwan/products/search?query=:relevance:allCategories:{category_id}&pageSize={page_size}&currentPage={page}&fields=FULL"
    req = urllib.request.Request(url, headers=headers)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                return data
        except Exception as e:
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))
            else:
                print(f"  [WARN] Failed fetching category {category_id} page {page}: {e}")
                return None

def main():
    args = parse_args()
    input_path = os.path.abspath(args.input)
    output_path = os.path.abspath(args.output)

    if not os.path.exists(input_path):
        print(f"[ERROR] Input manifest not found: {input_path}")
        return 1

    if os.path.exists(output_path) and not args.force:
        print(f"[SKIP] Output already exists at {output_path}. Use --force to rerun.")
        return 0

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(input_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    ctx = ssl._create_unverified_context()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'Accept-Language': 'zh-TW,zh;q=0.9',
    }

    products_by_code = {}
    categories_to_crawl = []

    # Always crawl root category '8'
    categories_to_crawl.append(("8", "食品飲料 (全分類根節點)"))

    # Also crawl major sub-branches to ensure no edge-case items are omitted
    primary_branches = [
        ("901", "飲料"),
        ("902", "零食"),
        ("907", "民生食材"),
        ("908", "冷凍冷藏"),
        ("909", "冷藏生鮮"),
        ("895", "Kirkland Signature 食品"),
        ("910", "Costco Frozen"),
        ("GCY913", "Costco Grocery 常溫食品")
    ]
    for cid, name in primary_branches:
        if (cid, name) not in categories_to_crawl:
            categories_to_crawl.append((cid, name))

    print(f"[*] Starting crawl across {len(categories_to_crawl)} key category trees...")
    start_time = time.time()

    for cid, name in categories_to_crawl:
        page = 0
        total_pages = 1
        cat_item_count = 0
        print(f"\n--- Crawling Category [{cid}] {name} ---")

        while page < total_pages:
            data = fetch_category_page(ctx, headers, cid, page=page, page_size=100)
            if not data:
                break

            pagination = data.get("pagination", {})
            total_pages = pagination.get("totalPages", 1)
            total_results = pagination.get("totalResults", 0)
            prods = data.get("products", [])

            new_in_page = 0
            for p in prods:
                code = str(p.get("code", "")).strip()
                if code:
                    if code not in products_by_code:
                        products_by_code[code] = p
                        new_in_page += 1
                    else:
                        # Merge category tags if available
                        existing_p = products_by_code[code]
                        if not existing_p.get("price") and p.get("price"):
                            existing_p["price"] = p.get("price")

            cat_item_count += len(prods)
            print(f"  Page {page + 1}/{total_pages} (Category Total: {total_results}): {len(prods)} items (+{new_in_page} new unique, Global Total: {len(products_by_code)})")
            page += 1
            time.sleep(0.3)

    elapsed = time.time() - start_time
    print(f"\n[SUCCESS] Crawl completed in {elapsed:.2f}s!")
    print(f"[SUMMARY] Total unique products harvested: {len(products_by_code)}")

    # Sort items deterministically by code
    raw_products_list = [products_by_code[k] for k in sorted(products_by_code.keys())]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(raw_products_list, f, ensure_ascii=False, indent=2)

    print(f"[OUTPUT] Saved raw products list to {output_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
