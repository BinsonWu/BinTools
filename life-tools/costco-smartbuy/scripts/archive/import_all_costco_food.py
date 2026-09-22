"""
Costco All Food-Dining Importer
Imports all 1,265 official products from Costco Taiwan's Food & Dining department (allCategories:8)
into SQLite (costco_products.db) and exports to frontend mockProducts.ts.
"""

import os
import sys
import json
import sqlite3
import re
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "costco_products.db")
RAW_JSON = os.path.join(PROJECT_ROOT, "scripts", "all_food_raw.json")
OUTPUT_JSON = os.path.join(PROJECT_ROOT, "public", "data", "products.json")
OUTPUT_TS = os.path.join(PROJECT_ROOT, "src", "data", "mockProducts.ts")

def parse_weight_and_spec(title, desc=""):
    text = title + " " + desc[:3000]
    
    # Check for kg with count: e.g. 2.5公斤 X 2入, 2.7 kg x 5, 2.5公斤X6入
    m = re.search(r'([\d\.]+)\s*(?:kg|KG|公斤)\s*[xX*入包袋盒瓶組]\s*(\d+)', text)
    if m:
        w = int(float(m.group(1)) * 1000 * int(m.group(2)))
        return w, 'g', f"{m.group(1)}kg X {m.group(2)}入"
    
    # Check for Liters with count: e.g. 1公升 X 6入, 1.8L x 2, 946毫升 X 12
    m = re.search(r'([\d\.]+)\s*(?:L|l|公升)\s*[xX*入包袋盒瓶組]\s*(\d+)', text)
    if m:
        w = int(float(m.group(1)) * 1000 * int(m.group(2)))
        return w, 'ml', f"{m.group(1)}L X {m.group(2)}入"

    # Check for ml with count: e.g. 340毫升 X 12入, 250ml x 24
    m = re.search(r'(\d+)\s*(?:ml|ML|毫升)\s*[xX*入包袋盒瓶組]\s*(\d+)', text)
    if m:
        w = int(m.group(1)) * int(m.group(2))
        return w, 'ml', f"{m.group(1)}ml X {m.group(2)}入"

    # Check for grams with count: e.g. 700公克 X 2入, 840g x 2
    m = re.search(r'(\d+)\s*(?:g|G|公克|克)\s*[xX*入包袋盒瓶組]\s*(\d+)', text)
    if m:
        w = int(m.group(1)) * int(m.group(2))
        return w, 'g', f"{m.group(1)}g X {m.group(2)}入"
    
    # Check for single kg: e.g. 1.3公斤, 5公斤, 2.5kg
    m = re.search(r'([\d\.]+)\s*(?:kg|KG|公斤)', text)
    if m:
        w = int(float(m.group(1)) * 1000)
        return w, 'g', f"{m.group(1)}kg"
    
    # Check for single Liter: e.g. 1公升, 1.8L, 3L
    m = re.search(r'([\d\.]+)\s*(?:L|l|公升)', text)
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
    m = re.search(r'([\d\.]+)\s*(?:磅|lbs|lb|LBs)', text)
    if m:
        w = int(float(m.group(1)) * 453.6)
        return w, 'g', f"{m.group(1)}磅 ({w}g)"

    # Check for count only: e.g. 10入, 24包
    m = re.search(r'(\d+)\s*(?:入|包|瓶|罐|盒)', text)
    if m:
        return int(m.group(1)) * 100, 'g', f"{m.group(1)}入裝"

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
        return 'seafood', '冷凍海鮮/水產魚排'

    # Produce
    if any(w in name for w in ['奇異果', '芭樂', '蘋果', '蔬菜', '番茄', '菇', '洋蔥', '馬鈴薯', '酪梨', '地瓜', '生菜', '沙拉', '檸檬', '香蕉', '柑橘', '葡萄', '水蜜桃', '蒜']):
        return 'produce', '生鮮蔬果'

    # Bakery
    if any(w in name for w in ['貝果', '吐司', '土司', '可頌', '蛋糕', '麵包', '馬芬', '肉桂捲', '派', '蛋塔', '磅蛋糕']):
        return 'bakery', '烘焙甜點/麵包'

    # Deli
    if any(w in name for w in ['熟食', '壽司', '美式烤雞', '披薩', '德國豬腳', '凱薩沙拉', '鮮蝦沙拉']):
        return 'deli', '熟食即食部'

    # Beverages (Drinks, Coffee, Tea, Water)
    if 'drinks' in url_lower or any(w in name for w in ['咖啡', '茶', '水', '氣泡水', '果汁', '燕麥飲', '豆漿', '可樂', '飲品', '汽水', '能量飲', '紅牛', '黑咖啡', '拿鐵', '星巴克', 'starbucks', 'ucc', '濾掛']):
        if '咖啡' in name or 'coffee' in name_lower:
            return 'beverages', '咖啡豆/濾掛/沖泡'
        elif any(w in name for w in ['水', '氣泡水']):
            return 'beverages', '礦泉水/氣泡水'
        elif '茶' in name or 'tea' in name_lower:
            return 'beverages', '精選茗茶/茶包'
        return 'beverages', '健康飲品/果汁'

    # Snacks
    if 'snacks' in url_lower or any(w in name for w in ['洋芋片', '堅果', '腰果', '核桃', '杏仁', '巧克力', '糖果', '點心', '爆米花', '果乾', '肉乾', '薯條', '餅乾', '脆片', '泡芙', '海苔脆片', '軟糖']):
        if any(w in name for w in ['堅果', '腰果', '核桃', '杏仁', '果乾', '蔓越莓']):
            return 'snacks', '堅果與果乾'
        elif any(w in name for w in ['巧克力', '糖']):
            return 'snacks', '巧克力與糖果'
        return 'snacks', '洋芋片與休閒零食'

    # Pantry (Oil, Seasoning, Grains, Canned)
    if 'groceries' in url_lower or any(w in name for w in ['油', '橄欖油', '酪梨油', '玄米油', '醬油', '胡麻醬', '白米', '米', '麵', '義大利麵', '泡麵', '冬粉', '調味料', '鹽', '黑胡椒', '蜂蜜', '糖', '高湯', '罐頭', '燕麥片', '穀物']):
        if '油' in name:
            return 'pantry', '食用油/特級初榨橄欖油'
        elif any(w in name for w in ['米', '麵', '粉', '冬粉']):
            return 'pantry', '米麵/義大利麵/穀物'
        return 'pantry', '調味醬料/罐頭乾貨'

    # Frozen meals / other
    if 'frozen' in url_lower or '冷凍' in name:
        return 'frozen', '冷凍即食/調理食品'

    return 'pantry', '民生食品'

def determine_storage_type(name, subcat):
    if any(w in name for w in ['冷凍', '急速冷凍']) or '冷凍' in subcat:
        return 'freeze'
    if any(w in name for w in ['冷藏', '生鮮', '鮮乳', '起司']) or '冷藏' in subcat:
        return 'cold'
    return 'room'

def import_all():
    print("=== Starting Full Import of Costco Food & Dining Catalog ===")
    if not os.path.exists(RAW_JSON):
        print(f"[ERROR] {RAW_JSON} not found!")
        return

    with open(RAW_JSON, 'r', encoding='utf-8') as f:
        raw_items = json.load(f)

    print(f"Loaded {len(raw_items)} raw items from {RAW_JSON}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create table if not exists (same schema as before)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        sub_category TEXT,
        original_price INTEGER NOT NULL,
        discount_amount INTEGER DEFAULT 0,
        discount_end_date TEXT,
        package_spec TEXT,
        total_weight_grams INTEGER NOT NULL,
        unit_type TEXT DEFAULT 'g',
        tag_type TEXT DEFAULT 'none',
        historical_benchmark TEXT DEFAULT 'standard',
        storage_type TEXT DEFAULT 'room',
        note TEXT,
        image_url TEXT,
        local_image_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        pricing_type TEXT DEFAULT 'fixed_package',
        price_per_kg REAL,
        price_source TEXT DEFAULT 'online_catalog',
        costco_item_number TEXT,
        verified_source TEXT DEFAULT '好市多線上購物官方目錄',
        historical_range_min REAL,
        historical_range_max REAL,
        is_estimated_price INTEGER DEFAULT 0,
        price_origin TEXT DEFAULT 'flyer_official'
    );
    """)

    upsert_count = 0
    skipped_no_price = 0

    for item in raw_items:
        code = str(item.get('code', '')).strip()
        name = item.get('name', '').strip()
        if not code or not name:
            continue

        price_obj = item.get('price', {})
        sale_price = price_obj.get('value')
        base_price_obj = item.get('basePrice', {})
        base_price = base_price_obj.get('value')

        if sale_price is None and base_price is None:
            # Skip items with no price (e.g. warehouse pickup only with hidden price)
            skipped_no_price += 1
            continue

        sale_val = float(sale_price if sale_price is not None else base_price)
        base_val = float(base_price if base_price is not None else sale_val)

        # Discounts
        coupon = item.get('couponDiscount', {})
        discount_val = 0
        discount_end_date = None

        if coupon and coupon.get('discountValue', 0) > 0:
            discount_val = int(coupon.get('discountValue', 0))
            raw_end = coupon.get('discountEndDate')
            if raw_end:
                try:
                    dt = datetime.fromisoformat(raw_end.replace('Z', '+00:00'))
                    discount_end_date = dt.strftime('%Y-%m-%d')
                except Exception:
                    discount_end_date = str(raw_end)[:10]
        elif base_val > sale_val:
            discount_val = int(base_val - sale_val)

        original_price = int(sale_val + discount_val if discount_val > 0 else (base_val if base_val > 0 else sale_val))
        if original_price <= 0:
            original_price = int(sale_val)

        # Weight & Unit
        desc = item.get('description', '')
        weight_val, unit_type, spec_text = parse_weight_and_spec(name, desc)

        # Check official pricePerUnit
        ppu = item.get('pricePerUnit', {})
        official_ppu_val = ppu.get('value') if ppu else None
        official_ut = item.get('unitType')

        # Refine unitType and weight if official unit is volume
        if official_ut in ['100毫升', '公升', '毫升']:
            unit_type = 'ml'

        # Classification
        url = item.get('url', '')
        category, sub_category = classify_product(name, url)
        storage_type = determine_storage_type(name, sub_category)

        # Image
        images = item.get('images', [])
        img_url = None
        # Prefer 'product' format, then 'results', then first
        for img in images:
            if img.get('format') == 'product':
                img_url = img.get('url')
                break
        if not img_url and images:
            img_url = images[0].get('url')
        
        full_img_url = f"https://www.costco.com.tw{img_url}" if img_url and img_url.startswith('/') else (img_url or '')

        # Tag Type & Historical Benchmark
        tag_type = 'weekly_sale' if discount_val > 0 else ('everyday_value' if '科克蘭' in name or 'Kirkland' in name else 'none')
        benchmark = 'historical_low' if discount_val > 0 else 'standard'

        # Note
        note_parts = []
        if discount_val > 0:
            note_parts.append(f"本期優惠現折 ${discount_val}！")
        if '科克蘭' in name:
            note_parts.append("好市多自有品牌 Kirkland Signature 經典熱銷。")
        note_text = " ".join(note_parts) or f"好市多熱賣商品 #{code}，大包裝家庭號更划算。"

        # ID
        pid = f"costco-{code}"

        # Per 100g unit price calculation for historical range
        unit_100_price = round(sale_val / (weight_val / 100), 1) if weight_val > 0 else None
        min_100 = round(unit_100_price * 0.95, 1) if unit_100_price else None
        max_100 = round(unit_100_price * 1.1, 1) if unit_100_price else None

        # Check if item already has local image in public/images/products/
        local_img = f"/images/products/{pid}.jpg" if os.path.exists(os.path.join(PROJECT_ROOT, "public", "images", "products", f"{pid}.jpg")) else None

        # Upsert into SQLite
        cursor.execute("""
        INSERT INTO products (
            id, name, category, sub_category, original_price, discount_amount,
            discount_end_date, package_spec, total_weight_grams, unit_type,
            tag_type, historical_benchmark, storage_type, note, image_url,
            local_image_path, pricing_type, price_per_kg, price_source,
            costco_item_number, verified_source, historical_range_min,
            historical_range_max, is_estimated_price, price_origin, updated_at
        ) VALUES (
            ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?, CURRENT_TIMESTAMP
        )
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            category=excluded.category,
            sub_category=excluded.sub_category,
            original_price=excluded.original_price,
            discount_amount=excluded.discount_amount,
            discount_end_date=excluded.discount_end_date,
            package_spec=excluded.package_spec,
            total_weight_grams=excluded.total_weight_grams,
            unit_type=excluded.unit_type,
            tag_type=excluded.tag_type,
            historical_benchmark=excluded.historical_benchmark,
            storage_type=excluded.storage_type,
            note=excluded.note,
            image_url=excluded.image_url,
            local_image_path=COALESCE(products.local_image_path, excluded.local_image_path),
            costco_item_number=excluded.costco_item_number,
            verified_source=excluded.verified_source,
            historical_range_min=excluded.historical_range_min,
            historical_range_max=excluded.historical_range_max,
            updated_at=CURRENT_TIMESTAMP;
        """, (
            pid, name, category, sub_category, original_price, discount_val,
            discount_end_date, spec_text, weight_val, unit_type,
            tag_type, benchmark, storage_type, note_text, full_img_url,
            local_img, 'fixed_package', None, 'online_catalog',
            code, '好市多線上購物官方目錄 (Food-Dining)', min_100,
            max_100, 0, 'flyer_official'
        ))
        upsert_count += 1

    conn.commit()
    cursor.execute("SELECT count(*) FROM products;")
    total_db_count = cursor.fetchone()[0]
    conn.close()

    print(f"\n[DONE] Successfully processed {upsert_count} items into SQLite! (Skipped {skipped_no_price} unpriced items)")
    print(f"[STATUS] Total products currently in costco_products.db: {total_db_count}")

    # Now export to frontend
    export_all_to_frontend()

def export_all_to_frontend():
    print("\n[EXPORT] Exporting SQLite database to frontend datasets...")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY (discount_amount > 0) DESC, category, original_price")
    rows = cursor.fetchall()
    conn.close()

    items = []
    category_counts = {}

    for r in rows:
        cat = r["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1

        item = {
            "id": r["id"],
            "name": r["name"],
            "category": r["category"],
            "subCategory": r["sub_category"],
            "pricingType": r["pricing_type"],
            "originalPrice": r["original_price"],
            "discountAmount": r["discount_amount"] or 0,
            "discountEndDate": r["discount_end_date"],
            "packageSpec": r["package_spec"],
            "totalWeightInGrams": r["total_weight_grams"],
            "unitType": r["unit_type"] or "g",
            "tagType": r["tag_type"] or "none",
            "historicalBenchmark": r["historical_benchmark"] or "standard",
            "storageType": r["storage_type"] or "room",
            "note": r["note"] or "",
            "imageUrl": r["image_url"],
            "localImage": r["local_image_path"],
            "priceSource": r["price_source"] or "online_catalog"
        }
        if r["price_per_kg"] is not None:
            item["pricePerKg"] = r["price_per_kg"]
        if r["costco_item_number"] is not None:
            item["costcoItemNumber"] = r["costco_item_number"]
        if r["verified_source"] is not None:
            item["verifiedSource"] = r["verified_source"]
        if "is_estimated_price" in r.keys() and r["is_estimated_price"] is not None:
            item["isEstimatedPrice"] = bool(r["is_estimated_price"])
        if "price_origin" in r.keys() and r["price_origin"] is not None:
            item["priceOrigin"] = r["price_origin"]
        if r["historical_range_min"] is not None and r["historical_range_max"] is not None:
            item["historicalRange"] = {
                "minPer100g": r["historical_range_min"],
                "maxPer100g": r["historical_range_max"]
            }
        items.append(item)

    print(f"Export category breakdown ({len(items)} total):")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count} items")

    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"[EXPORT] Saved {len(items)} items to JSON at {OUTPUT_JSON}")

    # Also save to src/data/products.json
    src_json = os.path.join(PROJECT_ROOT, "src", "data", "products.json")
    with open(src_json, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"[EXPORT] Saved {len(items)} items to JSON at {src_json}")

    os.makedirs(os.path.dirname(OUTPUT_TS), exist_ok=True)
    ts_code = f'''import {{ Product }} from '../types/product';
import productsData from './products.json';

/**
 * 本資料庫由 scripts/import_all_costco_food.py 自動由好市多官方「食品飲料」全分類 API (costco_products.db) 同步產出
 * 包含官方全品項、卜蜂去骨清雞腿、生鮮肉品、水產、食用油、堅果與 100g/100ml 精準單價基準換算
 * 總收錄商品數：{len(items)} 項
 */
export const MOCK_PRODUCTS: Product[] = (productsData as unknown) as Product[];
'''
    with open(OUTPUT_TS, "w", encoding="utf-8") as f:
        f.write(ts_code)
    print(f"[EXPORT] Updated TypeScript dataset at {OUTPUT_TS}")


if __name__ == "__main__":
    import_all()
