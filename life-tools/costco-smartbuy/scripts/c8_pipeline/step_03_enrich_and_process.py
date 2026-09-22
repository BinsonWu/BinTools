#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 03: Enrich and Process Costco Products
Accepts:
  --input: Path to c8_all_products_raw.json from Step 02
  --output: Target JSON path to save enriched processed products array
  --db: Optional path to costco_products.db to lookup historical/warehouse prices
  --force: Force overwrite output if exists
"""

import os
import sys
import json
import re
import sqlite3
import argparse
from datetime import datetime

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def parse_args():
    parser = argparse.ArgumentParser(description="Step 03: Enrich and process product catalog")
    parser.add_argument("--input", required=True, help="Input raw products JSON")
    parser.add_argument("--output", required=True, help="Target JSON output for processed products")
    parser.add_argument("--db", default="costco_products.db", help="Path to sqlite database for fallback prices")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing output")
    return parser.parse_args()

# Curated reference prices for classic Costco warehouse-only food staples
KNOWN_WAREHOUSE_PRICES = {
    "313088": {"price": 569, "source": "好市多賣場現場標價 (3.6kg 雙罐組)"},
    "204989": {"price": 399, "source": "好市多賣場現場標價 (44入隨身包)"},
    "743354": {"price": 439, "source": "好市多賣場現場標價 (10入大袋裝)"},
    "1964737": {"price": 219, "source": "好市多賣場現場標價 (1500ml x 12入)"},
    "193901": {"price": 799, "source": "好市多賣場現場標價 (約2.5kg火鍋片)"},
    "705188": {"price": 599, "source": "好市多賣場現場標價 (冷藏鱸魚排/包)"},
    "1602320": {"price": 239, "source": "好市多賣場現場標價 (374g研磨罐)"},
    "1550177": {"price": 549, "source": "好市多賣場現場標價 (1.07kg經典腰果)"},
    "1219113": {"price": 329, "source": "好市多賣場現場標價 (946ml x 3入組)"},
    "866581": {"price": 399, "source": "好市多賣場現場標價 (1.5kg冷凍草莓)"},
    "68714": {"price": 439, "source": "好市多賣場現場標價 (154g x 5入組)"},
    "78363": {"price": 329, "source": "好市多賣場現場標價 (300ml x 3入)"},
    "74345": {"price": 359, "source": "好市多賣場現場標價 (26g x 20包)"},
    "93920": {"price": 149, "source": "好市多賣場現場標價 (800g生菜包)"},
    "686035": {"price": 499, "source": "好市多賣場現場標價 (1.8kg白甜桃)"},
    "675645": {"price": 339, "source": "好市多賣場現場標價 (5g x 30入)"}
}

def parse_weight_and_spec(title, desc=""):
    text = title + " " + desc[:3000]

    try:
        # Check for kg with count: e.g. 2.5公斤 X 2入, 2.7 kg x 5, 2.5公斤X6入
        m = re.search(r'(\d+(?:\.\d+)?)\s*(?:kg|KG|公斤)\s*[xX*入包袋盒瓶組]\s*(\d+)', text)
        if m:
            w = int(float(m.group(1)) * 1000 * int(m.group(2)))
            return w, 'g', f"{m.group(1)}kg X {m.group(2)}入"

        # Check for Liters with count: e.g. 1公升 X 6入, 1.8L x 2, 946毫升 X 12
        m = re.search(r'(\d+(?:\.\d+)?)\s*(?:L|l|公升)\s*[xX*入包袋盒瓶組]\s*(\d+)', text)
        if m:
            w = int(float(m.group(1)) * 1000 * int(m.group(2)))
            return w, 'ml', f"{m.group(1)}L X {m.group(2)}入"

        # Check for ml with count: e.g. 340毫升 X 12入, 250ml x 24
        m = re.search(r'(\d+)\s*(?:ml|ML|毫升)\s*[xX*入包袋盒瓶組]\s*(\d+)', text)
        if m:
            w = int(m.group(1)) * int(m.group(2))
            return w, 'ml', f"{m.group(1)}ml X {m.group(2)}入"

        # Check for grams with count: e.g. 700公克 X 2入, 840g x 2, 37.5公克 X 44入
        m = re.search(r'(\d+(?:\.\d+)?)\s*(?:g|G|公克|克)\s*[xX*入包袋盒瓶組]\s*(\d+)', text)
        if m:
            w = int(float(m.group(1)) * int(m.group(2)))
            return w, 'g', f"{m.group(1)}g X {m.group(2)}入"

        # Check for single kg: e.g. 1.3公斤, 5公斤, 2.5kg, 3.6公斤
        m = re.search(r'(\d+(?:\.\d+)?)\s*(?:kg|KG|公斤)', text)
        if m:
            w = int(float(m.group(1)) * 1000)
            return w, 'g', f"{m.group(1)}kg"

        # Check for single Liter: e.g. 1公升, 1.8L, 3L
        m = re.search(r'(\d+(?:\.\d+)?)\s*(?:L|l|公升)', text)
        if m:
            w = int(float(m.group(1)) * 1000)
            return w, 'ml', f"{m.group(1)}L"

        # Check for single ml: e.g. 500毫升, 750ml
        m = re.search(r'(\d+)\s*(?:ml|ML|毫升)', text)
        if m:
            w = int(m.group(1))
            return w, 'ml', f"{m.group(1)}ml"

        # Check for single grams: e.g. 800公克, 600g
        m = re.search(r'(\d+)\s*(?:g|G|公克|克)', text)
        if m:
            w = int(m.group(1))
            return w, 'g', f"{m.group(1)}g"

        # Check for lbs: e.g. 2磅 / 908公克
        m = re.search(r'(\d+(?:\.\d+)?)\s*(?:磅|lbs|lb|LBs)', text)
        if m:
            w = int(float(m.group(1)) * 453.6)
            return w, 'g', f"{m.group(1)}磅 ({w}g)"

        # Check for count only: e.g. 10入, 24包
        m = re.search(r'(\d+)\s*(?:入|包|瓶|罐|盒)', text)
        if m:
            return int(m.group(1)) * 100, 'g', f"{m.group(1)}入裝"
    except Exception:
        pass

    return 1000, 'g', '標準單件規格'

def classify_product(name, url=""):
    url_lower = url.lower()
    name_lower = name.lower()

    # Dairy / Eggs
    if any(w in name for w in ['鮮乳', '牛奶', '起司', '乾酪', '乳酪', '優格', '奶粉', '奶油', '大豆卵磷脂', '雞蛋', '石安牧場', '鹹蛋黃']):
        return 'dairy', '乳品與蛋'

    # Chicken
    if any(w in name for w in ['雞肉', '雞腿', '去骨清雞腿', '清雞腿', '雞胸', '雞翅', '雞塊', '雞精', '雞排', '雞柳', '雞爪', '氣冷雞', '土雞', '烤雞', '香雞', '卜蜂', '大成', '元進莊']) and '調味料' not in name and '點心麵' not in name and '雞汁' not in name:
        if '腿' in name:
            return 'chicken', '生鮮雞腿/清雞腿'
        elif '胸' in name:
            return 'chicken', '生鮮雞胸肉'
        elif '翅' in name:
            return 'chicken', '雞翅/翅腿'
        return 'chicken', '生鮮禽肉/熟食調理'

    # Beef
    if any(w in name for w in ['牛肉', '牛排', '牛肋', '牛腱', '牛五花', '牛小排', '沙朗', '紐約克', '菲力', '和牛', '牛筋', '牛絞肉']):
        return 'beef', '冷藏/冷凍牛肉'

    # Pork / Lamb
    if any(w in name for w in ['豬肉', '五花肉', '松阪豬', '梅花肉', '豬肋排', '羊肉', '羊排', '培根', '火腿', '香腸', '豬腳', '伊比利豬', '黑豬']):
        return 'pork', '豬肉/羊肉'

    # Seafood
    if any(w in name for w in ['魚', '蝦', '干貝', '蟹', '海鮮', '鮭魚', '鯖魚', '吳郭魚', '海苔', '明太子', '魷魚', '鮑魚', '透抽', '鱸魚', '鮪魚', '鱈魚', '旗魚', '蒲燒']):
        return 'seafood', '海鮮水產'

    # Produce
    if any(w in name for w in ['奇異果', '芭樂', '蘋果', '蔬菜', '番茄', '菇', '洋蔥', '馬鈴薯', '酪梨', '地瓜', '生菜', '沙拉', '檸檬', '香蕉', '柑橘', '葡萄', '水蜜桃', '蒜', '白甜桃', '草莓', '哈密瓜']):
        return 'produce', '生鮮蔬果'

    # Bakery
    if any(w in name for w in ['貝果', '吐司', '土司', '可頌', '蛋糕', '麵包', '馬芬', '肉桂捲', '派', '蛋塔', '磅蛋糕']):
        return 'bakery', '烘焙甜點/麵包'

    # Deli
    if any(w in name for w in ['熟食', '壽司', '美式烤雞', '披薩', '德國豬腳', '凱薩沙拉', '鮮蝦沙拉']):
        return 'deli', '熟食即食部'

    # Beverages (Drinks, Coffee, Tea, Water, Oat Milk)
    if 'drinks' in url_lower or any(w in name for w in ['咖啡', '茶', '水', '氣泡水', '果汁', '燕麥飲', '燕麥奶', '豆漿', '可樂', '飲品', '汽水', '能量飲', '紅牛', '黑咖啡', '拿鐵', '星巴克', 'starbucks', 'ucc', '濾掛', '礦泉水']):
        if '咖啡' in name or 'coffee' in name_lower:
            return 'beverages', '咖啡豆/濾掛/沖泡'
        elif any(w in name for w in ['水', '氣泡水', '礦泉水']):
            return 'beverages', '礦泉水/氣泡水'
        elif '茶' in name or 'tea' in name_lower:
            return 'beverages', '精選茗茶/茶包'
        return 'beverages', '飲品/沖調'

    # Snacks
    if 'snacks' in url_lower or any(w in name for w in ['洋芋片', '堅果', '腰果', '核桃', '杏仁', '巧克力', '糖果', '點心', '爆米花', '果乾', '肉乾', '薯條', '餅乾', '脆片', '泡芙', '海苔脆片', '軟糖']):
        if any(w in name for w in ['堅果', '腰果', '核桃', '杏仁', '果乾', '蔓越莓']):
            return 'snacks', '堅果與果乾'
        elif any(w in name for w in ['巧克力', '糖']):
            return 'snacks', '巧克力與糖果'
        return 'snacks', '休閒零食'

    # Pantry (Oil, Seasoning, Grains, Canned, Oatmeal)
    if 'groceries' in url_lower or any(w in name for w in ['油', '橄欖油', '酪梨油', '玄米油', '醬油', '胡麻醬', '白米', '米', '麵', '義大利麵', '泡麵', '冬粉', '調味料', '鹽', '黑胡椒', '蜂蜜', '糖', '高湯', '罐頭', '燕麥片', '大燕麥片', '麥片', '穀物']):
        if '油' in name:
            return 'pantry', '食用油/調味油'
        elif any(w in name for w in ['米', '麵', '粉', '冬粉']):
            return 'pantry', '米麵穀物'
        elif any(w in name for w in ['燕麥片', '麥片', '大燕麥片']):
            return 'pantry', '燕麥片/即食穀物'
        return 'pantry', '調味醬料/罐頭食品'

    # Frozen
    if 'frozen' in url_lower or '冷凍' in name:
        return 'frozen', '冷凍調理/冷凍食品'

    return 'pantry', '生活食材'

def determine_storage_type(name, subcat):
    if any(w in name for w in ['冷凍', '急速冷凍']) or '冷凍' in subcat:
        return 'freeze'
    if any(w in name for w in ['冷藏', '生鮮', '鮮乳', '起司']) or '冷藏' in subcat:
        return 'cold'
    return 'room'

def load_existing_db_prices(db_path):
    prices = {}
    if not os.path.exists(db_path):
        return prices
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT id, original_price, verified_source, price_origin, pricing_type FROM products WHERE original_price > 0")
        for row in c.fetchall():
            prices[str(row[0])] = {
                "price": float(row[1]),
                "source": row[2] or "資料庫既有紀錄",
                "price_origin": row[3] or "store_tag",
                "pricing_type": row[4] or "fixed_package"
            }
        conn.close()
    except Exception as e:
        print(f"[WARN] Error reading existing DB prices: {e}")
    return prices

def main():
    args = parse_args()
    input_path = os.path.abspath(args.input)
    output_path = os.path.abspath(args.output)
    db_path = os.path.abspath(args.db)

    if not os.path.exists(input_path):
        print(f"[ERROR] Input raw file not found: {input_path}")
        return 1

    if os.path.exists(output_path) and not args.force:
        print(f"[SKIP] Output already exists at {output_path}. Use --force to rerun.")
        return 0

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(input_path, "r", encoding="utf-8") as f:
        raw_items = json.load(f)

    db_prices = load_existing_db_prices(db_path)
    print(f"[*] Loaded {len(raw_items)} raw items. Database price cache: {len(db_prices)} entries.")

    processed_list = []
    warehouse_only_count = 0
    enriched_price_count = 0

    for item in raw_items:
        code = str(item.get("code", "")).strip()
        name = item.get("name", "").strip()
        if not code or not name:
            continue

        price_obj = item.get("price", {})
        sale_price = price_obj.get("value")
        base_price_obj = item.get("basePrice", {})
        base_price = base_price_obj.get("value")

        price_source = "online_catalog"
        verified_source = "好市多線上購物官方目錄"
        price_origin = "flyer_official"
        is_estimated_price = False
        pricing_type = "fixed_package"
        original_price = 0
        discount_amount = 0
        discount_end_date = None

        if sale_price is not None or base_price is not None:
            sale_val = float(sale_price if sale_price is not None else base_price)
            base_val = float(base_price if base_price is not None else sale_val)

            coupon = item.get("couponDiscount", {})
            if coupon and coupon.get("discountValue", 0) > 0:
                discount_amount = int(coupon.get("discountValue", 0))
                raw_end = coupon.get("discountEndDate")
                if raw_end:
                    try:
                        dt = datetime.fromisoformat(raw_end.replace("Z", "+00:00"))
                        discount_end_date = dt.strftime("%Y-%m-%d")
                    except Exception:
                        discount_end_date = str(raw_end)[:10]
            elif base_val > sale_val:
                discount_amount = int(base_val - sale_val)

            original_price = base_val
        else:
            # Item has no online price (Warehouse-Only item)
            warehouse_only_count += 1
            price_source = "warehouse_only"

            if code in KNOWN_WAREHOUSE_PRICES:
                ref = KNOWN_WAREHOUSE_PRICES[code]
                original_price = float(ref["price"])
                verified_source = ref["source"]
                price_origin = "store_tag"
                is_estimated_price = False
                enriched_price_count += 1
            elif code in db_prices:
                ref = db_prices[code]
                original_price = float(ref["price"])
                verified_source = ref["source"]
                price_origin = ref["price_origin"]
                pricing_type = ref["pricing_type"]
                enriched_price_count += 1
            else:
                original_price = 0
                verified_source = "好市多賣場現場限定品 (線上未標價，歡迎點擊回報現場價)"
                price_origin = "store_tag"
                is_estimated_price = True

        desc = item.get("description", "") or ""
        total_weight, unit_type, package_spec = parse_weight_and_spec(name, desc)
        category, sub_category = classify_product(name, item.get("url", ""))
        storage_type = determine_storage_type(name, sub_category)

        # Image resolution
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

        # Check for local image
        local_img = None
        local_candidate = f"/daybuy_img/{code}.jpg"
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(output_path)))
        if os.path.exists(os.path.join(project_root, "public", "daybuy_img", f"{code}.jpg")):
            local_img = local_candidate

        # Tag types
        tag_type = "none"
        if discount_amount > 0:
            tag_type = "weekly_sale"
        elif "Kirkland" in name or "科克蘭" in name:
            tag_type = "everyday_value"

        product_record = {
            "id": code,
            "name": name,
            "category": category,
            "subCategory": sub_category,
            "pricingType": pricing_type,
            "originalPrice": original_price,
            "isEstimatedPrice": is_estimated_price,
            "priceOrigin": price_origin,
            "discountAmount": discount_amount,
            "discountEndDate": discount_end_date,
            "packageSpec": package_spec,
            "totalWeightInGrams": total_weight,
            "unitType": unit_type,
            "tagType": tag_type,
            "historicalBenchmark": "standard",
            "storageType": storage_type,
            "imageUrl": image_url,
            "localImage": local_img,
            "priceSource": price_source,
            "costcoItemNumber": code,
            "verifiedSource": verified_source,
            "note": "好市多賣場現場限定品" if price_source == "warehouse_only" else None
        }
        processed_list.append(product_record)

    print(f"\n[SUMMARY] Processed {len(processed_list)} total products:")
    print(f"  - Online Catalog Products: {len(processed_list) - warehouse_only_count}")
    print(f"  - Warehouse Only Products: {warehouse_only_count}")
    print(f"  - Enriched with Warehouse Prices: {enriched_price_count}")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(processed_list, f, ensure_ascii=False, indent=2)

    print(f"[OUTPUT] Saved processed products to {output_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
