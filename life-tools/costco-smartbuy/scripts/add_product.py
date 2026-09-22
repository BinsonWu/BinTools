"""
Costco Single Product Quick Importer & Updater
Usage:
    python scripts/add_product.py <Costco_URL_or_SKU> [category] [discount_amount]

Examples:
    python scripts/add_product.py https://www.costco.com.tw/Food-Dining/Frozen-Fresh-Food/Frozen-Seafood-Meat/ASC-Frozen-Tilapia-Fillet-13KG/p/484596
    python scripts/add_product.py 463663
"""

import sys
import os
import re
import ssl
import json
import sqlite3
import subprocess
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
DB_PATH = os.path.join(PROJECT_ROOT, "costco_products.db")
PUBLIC_IMG_DIR = os.path.join(PROJECT_ROOT, "public", "images", "products")
DIST_IMG_DIR = os.path.join(PROJECT_ROOT, "dist", "images", "products")
os.makedirs(PUBLIC_IMG_DIR, exist_ok=True)
os.makedirs(DIST_IMG_DIR, exist_ok=True)

def parse_weight_from_text(text):
    """Extract weight in grams or volume in ml from product title or description."""
    # Check for kg (e.g. 1.3kg, 1.3公斤, 2.7kg)
    m_kg = re.search(r'([\d\.]+)\s*(?:kg|KG|公斤)', text)
    if m_kg:
        return int(float(m_kg.group(1)) * 1000), 'g'
    
    # Check for grams with count (e.g. 700g X 2, 700公克 X 2入)
    m_multi_g = re.search(r'(\d+)\s*(?:g|G|公克)\s*[xX*]\s*(\d+)', text)
    if m_multi_g:
        return int(m_multi_g.group(1)) * int(m_multi_g.group(2)), 'g'

    # Check for grams (e.g. 800g, 480公克)
    m_g = re.search(r'(\d+)\s*(?:g|G|公克)', text)
    if m_g:
        return int(m_g.group(1)), 'g'

    # Check for liters (e.g. 1公升 X 6入, 2L)
    m_l = re.search(r'([\d\.]+)\s*(?:L|l|公升)\s*[xX*]\s*(\d+)', text)
    if m_l:
        return int(float(m_l.group(1)) * 1000 * int(m_l.group(2))), 'ml'

    m_single_l = re.search(r'([\d\.]+)\s*(?:L|l|公升)', text)
    if m_single_l:
        return int(float(m_single_l.group(1)) * 1000), 'ml'

    # Check for ml (e.g. 340ml X 12, 473毫升 X 6)
    m_multi_ml = re.search(r'(\d+)\s*(?:ml|ML|毫升)\s*[xX*]\s*(\d+)', text)
    if m_multi_ml:
        return int(m_multi_ml.group(1)) * int(m_multi_ml.group(2)), 'ml'

    m_ml = re.search(r'(\d+)\s*(?:ml|ML|毫升)', text)
    if m_ml:
        return int(m_ml.group(1)), 'ml'

    return 1000, 'g'

def add_or_update_product(url_or_sku, category=None, discount=0):
    # Extract SKU
    m_sku = re.search(r'/p/(\d+)', url_or_sku)
    sku = m_sku.group(1) if m_sku else url_or_sku.strip()
    if not sku.isdigit():
        print(f"[ERROR] Invalid SKU or URL: {url_or_sku}")
        return

    url = f"https://www.costco.com.tw/p/{sku}" if not url_or_sku.startswith("http") else url_or_sku
    print(f"\n[FETCH] Querying Costco Taiwan for SKU #{sku}...")

    # Fetch page
    ctx = ssl._create_unverified_context()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'Accept-Language': 'zh-TW,zh;q=0.9',
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"[ERROR] Failed to fetch product page: {e}")
        return

    # Extract metadata
    og_title = re.search(r'<meta\s+property=["\']og:title["\']\s+content=["\']([^"\']+)["\']', html)
    name = og_title.group(1).replace(' | Costco 好市多', '').strip() if og_title else f"Costco Item #{sku}"

    og_img = re.search(r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)["\']', html)
    img_url = og_img.group(1) if og_img else None
    if img_url and img_url.startswith("http://"):
        img_url = img_url.replace("http://", "https://")

    price_match = re.search(r'"price":\s*"([\d\.]+)"', html)
    sale_price = float(price_match.group(1)) if price_match else None

    # Check for discount text in page (e.g. 商品已折價 $100)
    discount_match = re.search(r'折價\s*\$?\s*(\d+)', html)
    if discount_match and discount == 0:
        discount = int(discount_match.group(1))

    if sale_price is None:
        print(f"[WARNING] Could not parse sale price automatically for #{sku}")
        sale_price = 0

    original_price = int(sale_price + discount)
    weight, unit_type = parse_weight_from_text(name + " " + html[:5000])

    # Category determination if not provided
    if not category:
        if any(w in name for w in ['魚', '蝦', '干貝', '蟹', '海鮮']):
            category = 'seafood'
        elif any(w in name for w in ['雞', '鴨', '鵝']):
            category = 'chicken'
        elif any(w in name for w in ['牛']):
            category = 'beef'
        elif any(w in name for w in ['豬']):
            category = 'pork'
        elif any(w in name for w in ['咖啡', '茶', '汁', '水', '飲']):
            category = 'pantry'
        elif any(w in name for w in ['冰淇淋', '起司', '奶', '乳']):
            category = 'dairy'
        else:
            category = 'pantry'

    pid = sku
    local_img = f"/images/products/{pid}.jpg"
    pub_img_path = os.path.join(PUBLIC_IMG_DIR, f"{pid}.jpg")
    dist_img_path = os.path.join(DIST_IMG_DIR, f"{pid}.jpg")

    # Download image if found
    if img_url:
        print(f"[IMAGE] Downloading official photo from {img_url}...")
        try:
            ret = subprocess.run(["curl.exe", "-L", "-k", "-s", "-o", pub_img_path, img_url], timeout=15)
            if ret.returncode == 0 and os.path.exists(pub_img_path) and os.path.getsize(pub_img_path) > 1000:
                subprocess.run(["curl.exe", "-L", "-k", "-s", "-o", dist_img_path, img_url], timeout=15)
                print(f"[IMAGE] Successfully saved to {local_img}")
        except Exception as e:
            print(f"[IMAGE] Warning: could not download image: {e}")

    # Calculate 100g unit prices
    p100_orig = round((original_price / weight) * 100, 1)
    p100_sale = round(((original_price - discount) / weight) * 100, 1)

    print("\n--- Parsed Product Details ---")
    print(f"SKU:           #{sku}")
    print(f"Name:          {name}")
    print(f"Category:      {category}")
    print(f"Weight:        {weight}{unit_type}")
    print(f"OriginalPrice: NT$ {original_price}")
    print(f"Discount:      NT$ {discount} -> Sale Price: NT$ {original_price - discount}")
    print(f"100g Price:    原價 NT$ {p100_orig} / 100{unit_type} -> 特價 NT$ {p100_sale} / 100{unit_type}")
    print("------------------------------\n")

    # Upsert into SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (
            id, name, category, pricing_type, original_price, discount_amount,
            package_spec, total_weight_grams, unit_type, tag_type, historical_benchmark,
            storage_type, price_source, costco_item_number, verified_source,
            is_estimated_price, price_origin, note, image_url, local_image_path, updated_at
        ) VALUES (?, ?, ?, 'fixed_package', ?, ?, ?, ?, ?, 'weekly_sale', 'historical_low',
                  'freeze', 'online_catalog', ?, '好市多官方商品頁面', 0, 'flyer_official',
                  ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            original_price=excluded.original_price,
            discount_amount=excluded.discount_amount,
            package_spec=excluded.package_spec,
            total_weight_grams=excluded.total_weight_grams,
            costco_item_number=excluded.costco_item_number,
            is_estimated_price=0,
            price_origin='flyer_official',
            local_image_path=excluded.local_image_path,
            updated_at=CURRENT_TIMESTAMP
    """, (
        pid, name, category, original_price, discount,
        f"{weight}{unit_type} 官方原裝規格", weight, unit_type,
        sku, f"好市多官方線上商品 #{sku}，原價 ${original_price}，每 100{unit_type} NT$ {p100_orig}！",
        img_url or "", local_img
    ))
    conn.commit()
    conn.close()
    print(f"[DB] Saved #{sku} into SQLite database 'costco_products.db'.")

    # Trigger frontend sync
    from scripts.costco_sync import export_to_frontend
    export_to_frontend()
    print(f"[SUCCESS] Product #{sku} is now live in the application!\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/add_product.py <Costco_URL_or_SKU> [category] [discount]")
        sys.exit(1)
    target = sys.argv[1]
    cat = sys.argv[2] if len(sys.argv) > 2 else None
    disc = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    add_or_update_product(target, cat, disc)
