#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 01: Discover Active Costco Promotion Channels
Strictly compliant with AGENTS.md

Accepts:
  --output: Target JSON path for promotional channels manifest
  --force: Force overwrite existing output
"""

import os
import sys
import json
import argparse
import urllib.request
import ssl
from datetime import datetime, timezone

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def parse_args():
    parser = argparse.ArgumentParser(description="Step 01: Discover promotional channels")
    parser.add_argument("--output", required=True, help="Target JSON output for promo channels manifest")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing output")
    return parser.parse_args()

PROMO_CATEGORIES_TO_INSPECT = [
    {"id": "hot-buys", "name": "線上熱門特惠 (Hot Buys)", "priority": 1},
    {"id": "Coupon", "name": "會員護照專案 / 優惠券 (Member Value Mailer)", "priority": 1},
    {"id": "featured-products", "name": "精選特價推薦 (Featured Deals)", "priority": 2},
    {"id": "hero-lowerprice", "name": "官方調降專區 (Lower Prices)", "priority": 2},
    {"id": "hero-sameprice", "name": "線上賣場同價特惠 (Same Price)", "priority": 2},
    {"id": "whats-new", "name": "最新上架優惠 (What's New)", "priority": 3}
]

def check_category_activity(ctx, headers, cat_id):
    url = f"https://www.costco.com.tw/rest/v2/taiwan/products/search?query=:relevance:allCategories:{cat_id}&pageSize=1"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=12) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pagination = data.get("pagination", {})
            return {
                "active": pagination.get("totalResults", 0) > 0,
                "total_results": pagination.get("totalResults", 0),
                "total_pages": pagination.get("totalPages", 0)
            }
    except Exception as e:
        print(f"  [WARN] Failed checking promo category {cat_id}: {e}")
        return {"active": False, "total_results": 0, "total_pages": 0}

def main():
    args = parse_args()
    output_path = os.path.abspath(args.output)

    if os.path.exists(output_path) and not args.force:
        print(f"[SKIP] Output already exists at {output_path}. Use --force to rerun.")
        return 0

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print("[*] Inspecting active Costco promotion channels...")

    ctx = ssl._create_unverified_context()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'Accept-Language': 'zh-TW,zh;q=0.9',
    }

    active_channels = []
    for cat in PROMO_CATEGORIES_TO_INSPECT:
        cid = cat["id"]
        cname = cat["name"]
        print(f"  Checking channel [{cid}] {cname}...", end=" ")
        stats = check_category_activity(ctx, headers, cid)
        if stats["active"]:
            print(f"ACTIVE ({stats['total_results']} items, {stats['total_pages']} pages)")
            active_channels.append({
                "id": cid,
                "name": cname,
                "priority": cat["priority"],
                "total_results": stats["total_results"],
                "total_pages": stats["total_pages"],
                "url": f"https://www.costco.com.tw/c/{cid}"
            })
        else:
            print("INACTIVE / 0 items")

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_active_channels": len(active_channels),
        "total_deals_count": sum(c["total_results"] for c in active_channels),
        "channels": active_channels
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"\n[SUCCESS] Step 01 finished. Found {len(active_channels)} active promo channels with {manifest['total_deals_count']} candidate deals.")
    print(f"[OUTPUT] Saved manifest to {output_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
