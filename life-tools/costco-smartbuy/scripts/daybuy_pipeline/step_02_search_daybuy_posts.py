#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 02: Search Daybuy.tw by SKU and Scrape Price Table and Photo URLs
Strictly compliant with AGENTS.md

Accepts:
  --input: Path to target_skus_manifest.json from Step 01
  --output: Target JSON path for scraped Daybuy results
  --force: Force overwrite existing output
"""

import os
import sys
import json
import time
import re
import argparse
import urllib.request
import ssl

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def parse_args():
    parser = argparse.ArgumentParser(description="Step 02: Search Daybuy posts by SKU")
    parser.add_argument("--input", required=True, help="Input target SKUs manifest JSON")
    parser.add_argument("--output", required=True, help="Target JSON output for scraped results")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing output")
    return parser.parse_args()

def fetch_url(ctx, headers, url, timeout=12):
    req = urllib.request.Request(url, headers=headers)
    for attempt in range(2):
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
                return resp.read().decode('utf-8', errors='ignore')
        except Exception:
            if attempt == 0:
                time.sleep(1)
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

    target_items = manifest.get("target_items", [])
    print(f"[*] Starting Daybuy search for {len(target_items)} target items...")

    ctx = ssl._create_unverified_context()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'Accept-Language': 'zh-TW,zh;q=0.9',
    }

    scraped_results = []
    found_count = 0

    # Cache for duplicate SKUs across different product records
    sku_cache = {}

    for idx, item in enumerate(target_items):
        sku = item["sku"]
        name = item["name"]
        print(f"[{idx + 1}/{len(target_items)}] Searching Daybuy for SKU #{sku} ({name[:20]})...", end=" ")

        if sku in sku_cache:
            res = dict(sku_cache[sku])
            res["productId"] = item["id"]
            scraped_results.append(res)
            print(f"(Cached) -> Found: {res.get('found', False)}")
            continue

        search_url = f"https://www.daybuy.tw/?s={sku}"
        html = fetch_url(ctx, headers, search_url)

        found_post = False
        post_url = None
        extracted_price = None
        historical_prices = []
        photo_images = []

        if html:
            # Look for costco post links: https://www.daybuy.tw/costco/(\d+)/
            post_links = re.findall(r'href=["\'](https://www\.daybuy\.tw/costco/\d+/)["\']', html)
            post_links = list(dict.fromkeys(post_links))

            if post_links:
                found_post = True
                post_url = post_links[0]
                post_html = fetch_url(ctx, headers, post_url)

                if post_html:
                    # 1. Extract prices from the table
                    raw_prices = re.findall(r'class="bdt-static-body-row-cell-text">\s*([0-9,]+)\s*元', post_html)
                    for rp in raw_prices:
                        try:
                            val = float(rp.replace(",", "").strip())
                            if val > 0:
                                historical_prices.append(val)
                        except Exception:
                            pass

                    if historical_prices:
                        extracted_price = historical_prices[0]

                    # 2. Extract photos (filter out logos and site banners)
                    raw_imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', post_html)
                    for img in raw_imgs:
                        if ('uploads' in img or 'daybuy' in img) and not any(k in img.lower() for k in ['logo', 'icon', 'banner', 'line_oa', 'facebook', 'avatar']):
                            if img.startswith('//'):
                                img = 'https:' + img
                            if img not in photo_images:
                                photo_images.append(img)

        if found_post and extracted_price:
            found_count += 1
            print(f"FOUND: NT$ {extracted_price} (Images: {len(photo_images)}) -> {post_url}")
        elif found_post:
            print(f"Post found, no price table -> {post_url}")
        else:
            print("Not found on Daybuy")

        result_entry = {
            "productId": item["id"],
            "sku": sku,
            "name": name,
            "found": found_post and (extracted_price is not None),
            "postUrl": post_url,
            "extractedPrice": extracted_price,
            "historicalPrices": historical_prices,
            "photoImages": photo_images
        }

        sku_cache[sku] = result_entry
        scraped_results.append(result_entry)
        time.sleep(0.3)

    output_data = {
        "total_searched": len(target_items),
        "total_prices_found": found_count,
        "results": scraped_results
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n[SUCCESS] Step 02 completed. Retrieved verified prices for {found_count} / {len(target_items)} items.")
    print(f"[OUTPUT] Saved scraped Daybuy results to {output_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
