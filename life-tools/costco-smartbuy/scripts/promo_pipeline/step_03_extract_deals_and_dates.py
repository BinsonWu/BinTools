#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 03: Extract Deals, Discount Amounts, End Dates, and 100g Savings
Strictly compliant with AGENTS.md

Accepts:
  --input: Path to raw_promo_products.json from Step 02
  --output: Target JSON path to save enriched deals list
  --force: Force overwrite existing output
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def parse_args():
    parser = argparse.ArgumentParser(description="Step 03: Extract deals and dates")
    parser.add_argument("--input", required=True, help="Input raw promo products JSON")
    parser.add_argument("--output", required=True, help="Target JSON output for enriched deals")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing output")
    return parser.parse_args()

def parse_weight_and_spec(title, desc=""):
    text = title + " " + desc[:2000]

    try:
        # Check for kg with count
        m = re.search(r'(\d+(?:\.\d+)?)\s*(?:kg|KG|公斤)\s*[xX*入包袋盒瓶組]\s*(\d+)', text)
        if m:
            w = int(float(m.group(1)) * 1000 * int(m.group(2)))
            return w, 'g', f"{m.group(1)}kg X {m.group(2)}入"

        # Check for Liters with count
        m = re.search(r'(\d+(?:\.\d+)?)\s*(?:L|l|公升)\s*[xX*入包袋盒瓶組]\s*(\d+)', text)
        if m:
            w = int(float(m.group(1)) * 1000 * int(m.group(2)))
            return w, 'ml', f"{m.group(1)}L X {m.group(2)}入"

        # Check for ml with count
        m = re.search(r'(\d+)\s*(?:ml|ML|毫升)\s*[xX*入包袋盒瓶組]\s*(\d+)', text)
        if m:
            w = int(m.group(1)) * int(m.group(2))
            return w, 'ml', f"{m.group(1)}ml X {m.group(2)}入"

        # Check for grams with count
        m = re.search(r'(\d+(?:\.\d+)?)\s*(?:g|G|公克|克)\s*[xX*入包袋盒瓶組]\s*(\d+)', text)
        if m:
            w = int(float(m.group(1)) * int(m.group(2)))
            return w, 'g', f"{m.group(1)}g X {m.group(2)}入"

        # Single kg
        m = re.search(r'(\d+(?:\.\d+)?)\s*(?:kg|KG|公斤)', text)
        if m:
            w = int(float(m.group(1)) * 1000)
            return w, 'g', f"{m.group(1)}kg"

        # Single Liter
        m = re.search(r'(\d+(?:\.\d+)?)\s*(?:L|l|公升)', text)
        if m:
            w = int(float(m.group(1)) * 1000)
            return w, 'ml', f"{m.group(1)}L"

        # Single ml
        m = re.search(r'(\d+)\s*(?:ml|ML|毫升)', text)
        if m:
            w = int(m.group(1))
            return w, 'ml', f"{m.group(1)}ml"

        # Single grams
        m = re.search(r'(\d+)\s*(?:g|G|公克|克)', text)
        if m:
            w = int(m.group(1))
            return w, 'g', f"{m.group(1)}g"

        # Count only
        m = re.search(r'(\d+)\s*(?:入|包|瓶|罐|盒)', text)
        if m:
            return int(m.group(1)) * 100, 'g', f"{m.group(1)}入裝"
    except Exception:
        pass

    return 1000, 'g', '標準單件規格'

def main():
    args = parse_args()
    input_path = os.path.abspath(args.input)
    output_path = os.path.abspath(args.output)

    if not os.path.exists(input_path):
        print(f"[ERROR] Input raw file not found: {input_path}")
        return 1

    if os.path.exists(output_path) and not args.force:
        print(f"[SKIP] Output already exists at {output_path}. Use --force to rerun.")
        return 0

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(input_path, "r", encoding="utf-8") as f:
        raw_items = json.load(f)

    print(f"[*] Processing {len(raw_items)} promotion products to extract discounts...")

    active_deals = []
    regular_promo_items = []

    for item in raw_items:
        code = str(item.get("code", "")).strip()
        name = item.get("name", "").strip()
        if not code or not name:
            continue

        price_obj = item.get("price", {})
        sale_price = price_obj.get("value")
        base_price_obj = item.get("basePrice", {})
        base_price = base_price_obj.get("value")

        coupon = item.get("couponDiscount", {}) or {}
        coupon_val = float(coupon.get("discountValue", 0))
        coupon_end = coupon.get("discountEndDate")

        discount_amount = 0
        discount_end_date = None

        # Determine original price and discount
        sale_val = float(sale_price if sale_price is not None else base_price if base_price is not None else 0)
        base_val = float(base_price if base_price is not None else sale_val)

        if coupon_val > 0:
            discount_amount = int(coupon_val)
            original_price = base_val
            if coupon_end:
                try:
                    dt = datetime.fromisoformat(coupon_end.replace("Z", "+00:00"))
                    discount_end_date = dt.strftime("%Y-%m-%d")
                except Exception:
                    discount_end_date = str(coupon_end)[:10]
        elif base_val > sale_val and sale_val > 0:
            discount_amount = int(base_val - sale_val)
            original_price = base_val
        else:
            original_price = sale_val

        # Spec and weight
        desc = item.get("description", "") or ""
        total_weight, unit_type, package_spec = parse_weight_and_spec(name, desc)

        # 100g savings calculation
        current_price = max(0, original_price - discount_amount)
        if total_weight > 0 and original_price > 0:
            orig_100g = round((original_price / total_weight) * 100, 1)
            curr_100g = round((current_price / total_weight) * 100, 1)
            savings_100g = max(0, round(orig_100g - curr_100g, 1))
            discount_percent = round((discount_amount / original_price) * 100) if discount_amount > 0 else 0
        else:
            savings_100g = 0
            discount_percent = 0

        # Tag type
        promo_channels = item.get("_promo_channels", [])
        tag_type = "none"
        if discount_amount > 0:
            tag_type = "weekly_sale"
        elif "Wallet" in promo_channels:
            tag_type = "black_card"
        elif "hero-lowerprice" in promo_channels or "Kirkland" in name or "科克蘭" in name:
            tag_type = "everyday_value"

        # Image
        images = item.get("images", [])
        image_url = None
        for img in images:
            if img.get("format") == "superZoom":
                image_url = img.get("url")
                break
        if not image_url and images:
            image_url = images[0].get("url")
        if image_url and not image_url.startswith("http"):
            image_url = "https://www.costco.com.tw" + image_url

        deal_record = {
            "id": code,
            "name": name,
            "originalPrice": original_price,
            "currentPrice": current_price,
            "discountAmount": discount_amount,
            "discountEndDate": discount_end_date,
            "isDiscounted": discount_amount > 0,
            "discountPercent": discount_percent,
            "packageSpec": package_spec,
            "totalWeightInGrams": total_weight,
            "unitType": unit_type,
            "savingsPer100g": savings_100g,
            "tagType": tag_type,
            "imageUrl": image_url,
            "promoChannels": promo_channels,
            "costcoItemNumber": code
        }

        if discount_amount > 0:
            active_deals.append(deal_record)
        else:
            regular_promo_items.append(deal_record)

    # Sort active deals by discount amount descending
    active_deals.sort(key=lambda d: d["discountAmount"], reverse=True)

    result_payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_promo_items": len(raw_items),
        "total_active_discounts": len(active_deals),
        "active_deals": active_deals,
        "other_promo_items": regular_promo_items
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_payload, f, ensure_ascii=False, indent=2)

    print(f"\n[SUMMARY] Deals Extraction Result:")
    print(f"  - Total Candidates Inspected: {len(raw_items)}")
    print(f"  - Verified Active Cash Discounts: {len(active_deals)}")
    for d in active_deals[:5]:
        print(f"    * #{d['id']}: {d['name'][:25]} -> 折 NT$ {d['discountAmount']} (省 {d['discountPercent']}%, 每100{d['unitType']}省 ${d['savingsPer100g']}) [至 {d['discountEndDate']}]")

    print(f"[OUTPUT] Saved enriched deals to {output_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
