#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 03: Download Store Photos and Enrich Product Metadata
Strictly compliant with AGENTS.md

Accepts:
  --input: Path to daybuy_scraped_results.json from Step 02
  --output: Target JSON path for verified products updates
  --public-img-dir: Target local images directory
  --force: Force overwrite existing output
"""

import os
import sys
import json
import re
import shutil
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
    parser = argparse.ArgumentParser(description="Step 03: Download photos and enrich metadata")
    parser.add_argument("--input", required=True, help="Input scraped Daybuy results JSON")
    parser.add_argument("--output", required=True, help="Target JSON output for verified updates")
    parser.add_argument("--public-img-dir", default="public/images/products", help="Local directory for product images")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing output")
    return parser.parse_args()

def download_image(ctx, headers, img_url, dest_path):
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1000:
        return True
    try:
        req = urllib.request.Request(img_url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            data = resp.read()
            if len(data) > 1000:
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                with open(dest_path, "wb") as f:
                    f.write(data)
                return True
    except Exception as e:
        print(f"    [WARN] Failed to download {img_url}: {e}")
    return False

def main():
    args = parse_args()
    input_path = os.path.abspath(args.input)
    output_path = os.path.abspath(args.output)
    img_dir = os.path.abspath(args.public_img_dir)

    if not os.path.exists(input_path):
        print(f"[ERROR] Input scraped file not found: {input_path}")
        return 1

    if os.path.exists(output_path) and not args.force:
        print(f"[SKIP] Output already exists at {output_path}. Use --force to rerun.")
        return 0

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)

    dist_img_dir = os.path.join(os.path.dirname(os.path.dirname(img_dir)), "dist", "images", "products")
    if os.path.exists(dist_img_dir):
        os.makedirs(dist_img_dir, exist_ok=True)

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = data.get("results", [])
    print(f"[*] Processing {len(results)} scraped Daybuy items and downloading verified photos...")

    ctx = ssl._create_unverified_context()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'Referer': 'https://www.daybuy.tw/',
    }

    verified_updates = []
    photos_downloaded = 0

    for item in results:
        pid = item["productId"]
        sku = item["sku"]
        name = item["name"]

        if not item.get("found") or not item.get("extractedPrice"):
            continue

        price = float(item["extractedPrice"])
        post_url = item.get("postUrl", "")
        post_id = re.search(r'/costco/(\d+)/', post_url)
        post_id_str = f"#{post_id.group(1)}" if post_id else ""

        # Historical range
        hist_prices = item.get("historicalPrices", [])
        hist_min = min(hist_prices) if hist_prices else price
        hist_max = max(hist_prices) if hist_prices else price

        # Download photo
        photo_images = item.get("photoImages", [])
        local_img_path = None
        img_url_to_use = None

        if photo_images:
            # Pick first high-res product/tag photo
            img_url_to_use = photo_images[0]
            dest_file = os.path.join(img_dir, f"daybuy_{sku}.jpg")

            if download_image(ctx, headers, img_url_to_use, dest_file):
                local_img_path = f"/images/products/daybuy_{sku}.jpg"
                photos_downloaded += 1
                # Copy to dist if dist exists
                if os.path.exists(dist_img_dir):
                    try:
                        shutil.copy2(dest_file, os.path.join(dist_img_dir, f"daybuy_{sku}.jpg"))
                    except Exception:
                        pass

        verified_updates.append({
            "productId": pid,
            "sku": sku,
            "name": name,
            "verifiedPrice": price,
            "postUrl": post_url,
            "postRef": post_id_str,
            "verifiedSource": f"今購百科 賣場現場標價牌實拍 ({post_id_str})",
            "historicalMin": hist_min,
            "historicalMax": hist_max,
            "localImagePath": local_img_path,
            "remoteImageUrl": img_url_to_use
        })

    output_payload = {
        "total_verified": len(verified_updates),
        "photos_downloaded": photos_downloaded,
        "verified_updates": verified_updates
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, ensure_ascii=False, indent=2)

    print(f"\n[SUMMARY] Download and Enrichment Result:")
    print(f"  - Verified Products with Real Prices: {len(verified_updates)}")
    print(f"  - Real Store Photos Downloaded: {photos_downloaded}")
    for u in verified_updates[:5]:
        print(f"    * #{u['sku']}: {u['name']} -> NT$ {u['verifiedPrice']} | {u['verifiedSource']}")

    print(f"[OUTPUT] Saved verified updates to {output_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
