#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 02: Crawl All Products in Active Costco Promotion Channels
Strictly compliant with AGENTS.md

Accepts:
  --input: Path to promo_channels_manifest.json from Step 01
  --output: Target JSON path to save raw promotional products
  --force: Force overwrite existing output
"""

import os
import sys
import json
import time
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
    parser = argparse.ArgumentParser(description="Step 02: Crawl promotion products")
    parser.add_argument("--input", required=True, help="Input channels manifest JSON")
    parser.add_argument("--output", required=True, help="Target JSON output for raw promo products")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing output")
    return parser.parse_args()

def fetch_channel_page(ctx, headers, channel_id, page=0, page_size=100):
    url = f"https://www.costco.com.tw/rest/v2/taiwan/products/search?query=:relevance:allCategories:{channel_id}&pageSize={page_size}&currentPage={page}&fields=FULL"
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
                print(f"  [WARN] Failed fetching channel {channel_id} page {page}: {e}")
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
    channels = manifest.get("channels", [])

    print(f"[*] Starting crawl across {len(channels)} active promotional channels...")
    t0 = time.time()

    for ch in channels:
        cid = ch["id"]
        cname = ch["name"]
        print(f"\n--- Channel: [{cid}] {cname} ---")

        page = 0
        total_pages = ch.get("total_pages", 1)

        while page < total_pages:
            data = fetch_channel_page(ctx, headers, cid, page=page, page_size=100)
            if not data:
                break

            pagination = data.get("pagination", {})
            total_pages = pagination.get("totalPages", 1)
            prods = data.get("products", [])

            new_count = 0
            for p in prods:
                code = str(p.get("code", "")).strip()
                if code:
                    if code not in products_by_code:
                        p["_promo_channels"] = [cid]
                        products_by_code[code] = p
                        new_count += 1
                    else:
                        if cid not in products_by_code[code].get("_promo_channels", []):
                            products_by_code[code]["_promo_channels"].append(cid)
                        # Retain richer coupon data if present
                        if not products_by_code[code].get("couponDiscount") and p.get("couponDiscount"):
                            products_by_code[code]["couponDiscount"] = p.get("couponDiscount")

            print(f"  Page {page + 1}/{total_pages}: {len(prods)} items (+{new_count} new unique, Global Deals: {len(products_by_code)})")
            page += 1
            time.sleep(0.3)

    elapsed = time.time() - t0
    print(f"\n[SUCCESS] Crawl completed in {elapsed:.2f}s!")
    print(f"[SUMMARY] Total unique promotional products gathered: {len(products_by_code)}")

    raw_promo_list = [products_by_code[k] for k in sorted(products_by_code.keys())]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(raw_promo_list, f, ensure_ascii=False, indent=2)

    print(f"[OUTPUT] Saved raw promo products to {output_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
