#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 01: Crawl Costco Taiwan Warehouse-Only (WH08) and Uber Eats (uber-only) products
Accepts:
  --output: Target JSON file path
  --force: Overwrite existing output
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import ssl
from datetime import datetime

# Windows encoding safety
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def parse_args():
    parser = argparse.ArgumentParser(description="Step 01: Crawl Warehouse-Only & Uber Eats products")
    parser.add_argument("--output", required=True, help="Path to save raw warehouse products JSON")
    parser.add_argument("--force", action="store_true", help="Force overwrite output if exists")
    return parser.parse_args()

def fetch_category_page(query, page_num=0, page_size=60):
    ctx = ssl._create_unverified_context()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    }
    encoded_query = urllib.request.quote(query, safe=':')
    url = f"https://www.costco.com.tw/rest/v2/taiwan/products/search?fields=FULL&query={encoded_query}&pageSize={page_size}&currentPage={page_num}"
    
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ctx, timeout=25) as resp:
        return json.loads(resp.read().decode('utf-8'))

def crawl_query_products(query_str, label):
    print(f"[*] Crawling category query [{label}] ({query_str})...")
    page = 0
    total_pages = 1
    items = []
    
    while page < total_pages:
        retries = 3
        data = None
        while retries > 0:
            try:
                data = fetch_category_page(query_str, page_num=page, page_size=60)
                break
            except Exception as e:
                retries -= 1
                print(f"[WARN] Error fetching page {page} for {label} ({e}), retrying ({retries} left)...")
                time.sleep(2)
        
        if not data:
            print(f"[ERROR] Failed to fetch page {page} for {label}")
            break
            
        pagination = data.get('pagination', {})
        total_pages = pagination.get('totalPages', 1)
        total_results = pagination.get('totalResults', 0)
        batch = data.get('products', [])
        
        items.extend(batch)
        print(f"  [{label}] Page {page + 1}/{total_pages}: fetched {len(batch)} items (accumulated: {len(items)}/{total_results})")
        
        page += 1
        time.sleep(0.3)
        
    return items

def main():
    args = parse_args()
    output_path = os.path.abspath(args.output)
    
    if os.path.exists(output_path) and not args.force:
        print(f"[SKIP] Output already exists at {output_path}. Use --force to rerun.")
        return 0
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    target_queries = [
        (":relevance:allCategories:WH08", "WH08_Food_Beverages"),
        (":relevance:allCategories:uber-only", "Uber_Eats_Only"),
    ]
    
    all_products = {}
    for query_str, label in target_queries:
        products = crawl_query_products(query_str, label)
        for p in products:
            code = str(p.get('code', '')).strip()
            if not code:
                continue
            if code not in all_products:
                all_products[code] = p
                all_products[code]['source_categories'] = [label]
            else:
                if label not in all_products[code]['source_categories']:
                    all_products[code]['source_categories'].append(label)
                    
    results = list(all_products.values())
    print(f"\n[SUCCESS] Step 01 finished. Deduplicated {len(results)} total warehouse-only / Uber Eats products.")
    
    manifest = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_count": len(results),
        "products": results
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        
    print(f"[OUTPUT] Saved raw warehouse products to {output_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
