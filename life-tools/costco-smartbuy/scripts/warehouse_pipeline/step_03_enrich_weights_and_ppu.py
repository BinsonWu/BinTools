#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 03: Enrich Weights, Package Specs, and PPU (Price Per Unit) for Warehouse Products
Accepts:
  --raw-products: Path to raw warehouse products JSON (from step 01)
  --daybuy-prices: Path to matched Daybuy store prices JSON (from step 02)
  --output: Target JSON file path
  --force: Overwrite existing output
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime

# Windows encoding safety
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def parse_args():
    parser = argparse.ArgumentParser(description="Step 03: Enrich weights and PPU")
    parser.add_argument("--raw-products", required=True, help="Path to raw warehouse products JSON")
    parser.add_argument("--daybuy-prices", required=True, help="Path to matched Daybuy prices JSON")
    parser.add_argument("--output", required=True, help="Target enriched products JSON output")
    parser.add_argument("--force", action="store_true", help="Force overwrite output if exists")
    return parser.parse_args()

def extract_weight_grams(name, desc, daybuy_weight_text=""):
    combined = f"{name} {desc} {daybuy_weight_text or ''}"
    
    # Check for multiplier patterns: 2.5公斤 X 2入, 50公克 X 24入, 1.13公斤 X 2入
    m_mult_kg = re.search(r'(\d+(?:\.\d+)?)\s*(?:公斤|kg)\s*[xX*]\s*(\d+)', combined, re.IGNORECASE)
    if m_mult_kg:
        try:
            return int(float(m_mult_kg.group(1)) * 1000 * int(m_mult_kg.group(2)))
        except ValueError:
            pass

    m_mult_g = re.search(r'(\d+(?:\.\d+)?)\s*(?:公克|克|g)\s*[xX*]\s*(\d+)', combined, re.IGNORECASE)
    if m_mult_g:
        try:
            return int(float(m_mult_g.group(1)) * int(m_mult_g.group(2)))
        except ValueError:
            pass

    # Check for single weight: 約淨重2.8公斤, 2.75KG, 500公克
    m_kg = re.search(r'(\d+(?:\.\d+)?)\s*(?:公斤|kg)', combined, re.IGNORECASE)
    if m_kg:
        try:
            return int(float(m_kg.group(1)) * 1000)
        except ValueError:
            pass

    m_g = re.search(r'(\d+(?:\.\d+)?)\s*(?:公克|克|g)\s*(?![a-zA-Z])', combined, re.IGNORECASE)
    if m_g:
        try:
            return int(float(m_g.group(1)))
        except ValueError:
            pass

    # ml patterns
    m_mult_ml = re.search(r'(\d+(?:\.\d+)?)\s*(?:毫升|ml)\s*[xX*]\s*(\d+)', combined, re.IGNORECASE)
    if m_mult_ml:
        try:
            return int(float(m_mult_ml.group(1)) * int(m_mult_ml.group(2)))
        except ValueError:
            pass

    m_ml = re.search(r'(\d+(?:\.\d+)?)\s*(?:毫升|ml)', combined, re.IGNORECASE)
    if m_ml:
        try:
            return int(float(m_ml.group(1)))
        except ValueError:
            pass

    return 1000 # default fallback 1kg

def determine_category(name, desc, cats):
    text = f"{name} {desc} {' '.join(cats)}"
    if any(k in text for k in ['牛排', '牛肉', '牛腱', '牛五花', '雞腿', '雞胸', '雞肉', '豬肉', '豬排', '羊肉', '羊排', '鮭魚', '干貝', '蝦', '海鮮', '鱸魚']):
        return '肉品海鮮'
    if any(k in text for k in ['壽司', '烤雞', '熱狗', '牛肉卷', '披薩', '三明治', '沙拉', '熟食', '濃湯']):
        return '生鮮熟食'
    if any(k in text for k in ['麵包', '蛋糕', '可頌', '貝果', '土司', '吐司', '派', '奶酥', '甜點', '糕點', '餅乾']):
        return '烘焙甜點'
    if any(k in text for k in ['牛奶', '鮮乳', '優格', '起司', '乾酪', '乳酪', '奶油', '蛋']):
        return '乳品蛋類'
    if any(k in text for k in ['蘋果', '櫻桃', '葡萄', '香蕉', '奇異果', '芭樂', '蔬菜', '生菜', '洋蔥', '番茄']):
        return '生鮮蔬果'
    if any(k in text for k in ['咖啡', '茶', '果汁', '汽水', '水', '飲品', '可樂', '酒', '啤酒', '紅酒']):
        return '飲料冰品'
    return '食品飲料'

def determine_storage_type(name, desc):
    text = f"{name} {desc}"
    if '冷凍' in text:
        return 'frozen'
    if '冷藏' in text or '保鮮' in text:
        return 'cold'
    return 'room'

def main():
    args = parse_args()
    raw_path = os.path.abspath(args.raw_products)
    daybuy_path = os.path.abspath(args.daybuy_prices)
    output_path = os.path.abspath(args.output)

    if not os.path.exists(raw_path) or not os.path.exists(daybuy_path):
        print(f"[ERROR] Required input files missing.")
        return 1

    if os.path.exists(output_path) and not args.force:
        print(f"[SKIP] Output already exists at {output_path}. Use --force to rerun.")
        return 0

    with open(raw_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
        raw_products = raw_data.get('products', [])

    with open(daybuy_path, 'r', encoding='utf-8') as f:
        daybuy_data = json.load(f)
        daybuy_matched = daybuy_data.get('matched_products', {})

    print(f"[*] Step 03: Enriching {len(raw_products)} warehouse products...")

    enriched = []
    by_weight_count = 0
    verified_tag_count = 0

    for p in raw_products:
        sku = str(p.get('code', '')).strip()
        if not sku:
            continue

        name = p.get('name', '').strip()
        desc = p.get('description', '') or ''
        cats = [c.get('code', '') for c in p.get('categories', [])]

        # Images
        imgs = p.get('images', [])
        official_img = None
        if imgs:
            for img in imgs:
                if img.get('format') in ['superZoom', 'zoom', 'product']:
                    url = img.get('url', '')
                    if url:
                        official_img = f"https://www.costco.com.tw{url}" if url.startswith('/') else url
                        break
            if not official_img and imgs[0].get('url'):
                url = imgs[0].get('url')
                official_img = f"https://www.costco.com.tw{url}" if url.startswith('/') else url

        daybuy_info = daybuy_matched.get(sku, {})
        local_img = daybuy_info.get('local_image_path')

        # Pricing & Weight resolution
        is_by_weight = daybuy_info.get('is_by_weight', False)
        price_per_kg = daybuy_info.get('price_per_kg')
        fixed_price = daybuy_info.get('fixed_price')
        post_id = daybuy_info.get('post_id')

        # Also detect by_weight from product name if '秤重' or '稱重'
        if not is_by_weight and any(k in f"{name} {desc}" for k in ['秤重', '稱重']):
            if price_per_kg:
                is_by_weight = True

        total_weight_grams = extract_weight_grams(name, desc, daybuy_info.get('weight_text'))

        original_price = 0
        pricing_type = 'fixed_package'
        is_estimated_price = 1
        price_origin = 'store_tag'
        verified_source = None

        if is_by_weight and price_per_kg and price_per_kg > 0:
            pricing_type = 'by_weight'
            by_weight_count += 1
            verified_tag_count += 1
            is_estimated_price = 0
            verified_source = f"今購百科 賣場現場標價牌實拍 (#{post_id})" if post_id else "好市多賣場現場秤重標價牌"
            # Calculate total package price based on standard packaging weight
            original_price = int(round(price_per_kg * (total_weight_grams / 1000.0)))
        elif fixed_price and fixed_price > 0:
            pricing_type = 'fixed_package'
            original_price = int(round(fixed_price))
            is_estimated_price = 0
            verified_tag_count += 1
            verified_source = f"今購百科 賣場現場標價牌實拍 (#{post_id})" if post_id else "好市多賣場現場實拍標價牌"
        else:
            # Check if official API has price
            p_price = p.get('price', {})
            if p_price and p_price.get('value'):
                original_price = int(round(p_price.get('value')))
                is_estimated_price = 0
                price_origin = 'online'
                verified_source = '好市多官方線上標價'

        category = determine_category(name, desc, cats)
        storage_type = determine_storage_type(name, desc)

        # Package spec string
        if pricing_type == 'by_weight':
            package_spec = f"約 {(total_weight_grams / 1000.0):.1f}kg (秤重商品)"
        else:
            package_spec = f"{(total_weight_grams / 1000.0):.2f}kg" if total_weight_grams >= 1000 else f"{total_weight_grams}g"

        prod_record = {
            "id": sku,
            "name": name,
            "category": category,
            "subCategory": '賣場限定 / Uber Eats',
            "originalPrice": original_price,
            "discountAmount": 0,
            "discountEndDate": None,
            "packageSpec": package_spec,
            "totalWeightInGrams": total_weight_grams,
            "unitType": "g",
            "tagType": "none",
            "historicalBenchmark": "standard",
            "storageType": storage_type,
            "note": "好市多賣場限定商品 / Uber Eats 熱賣" if 'uber-only' in p.get('source_categories', []) else "好市多賣場限定商品",
            "imageUrl": official_img or (local_img or "/images/products/placeholder.jpg"),
            "localImage": local_img,
            "pricingType": pricing_type,
            "pricePerKg": float(price_per_kg) if (pricing_type == 'by_weight' and price_per_kg) else None,
            "priceSource": "warehouse_only",
            "costcoItemNumber": sku,
            "verifiedSource": verified_source,
            "isEstimatedPrice": is_estimated_price,
            "priceOrigin": price_origin,
            "historicalRange": None
        }
        enriched.append(prod_record)

    manifest = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_enriched": len(enriched),
        "by_weight_count": by_weight_count,
        "verified_tag_count": verified_tag_count,
        "products": enriched
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"\n[SUCCESS] Step 03 finished. Enriched {len(enriched)} products:")
    print(f"  - By weight products: {by_weight_count}")
    print(f"  - Verified with Daybuy/store tag: {verified_tag_count}")
    print(f"[OUTPUT] Saved to {output_path}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
