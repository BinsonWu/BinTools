import os
import sys
import sqlite3
import subprocess
import shutil
import json

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

DB_PATH = os.path.join(PROJECT_ROOT, "costco_products.db")
PUB_IMG = os.path.join(PROJECT_ROOT, "public", "images", "products")
DIST_IMG = os.path.join(PROJECT_ROOT, "dist", "images", "products")
os.makedirs(PUB_IMG, exist_ok=True)
os.makedirs(DIST_IMG, exist_ok=True)

# 1. Download official Costco clean studio photos
official_items = [
    {
        "id": "chicken-02",
        "code": "118583",
        "name": "冷藏台灣去骨清雞腿真空包",
        "filename": "chicken-02.jpg",
        "costco_img": "https://www.costco.com.tw/medias/sys_master/images/h92/hea/120613020139550.jpg",
        "price_per_kg": 245.0,
        "original_price": 674, # 2.75kg * 245
        "package_spec": "2.75kg (單包約6小包，賣場原牌價 $245/kg)",
        "total_weight_grams": 2750,
        "note": "好市多門市冷藏生鮮去骨清雞腿真空包（原肉獨立小袋包），今購百科門市實拍原牌價為每公斤 $245（換算每 100g 為 NT$ 24.5，每台斤約 NT$ 147）。"
    },
    {
        "id": "chicken-01",
        "code": "110478",
        "name": "台灣雞清胸肉真空包 (生鮮冷藏)",
        "filename": "chicken-01.jpg",
        "costco_img": "https://www.costco.com.tw/medias/sys_master/images/h02/h6e/47403179573278.jpg",
        "price_per_kg": 215.0,
        "original_price": 580, # 2.7kg * 215
        "package_spec": "2.7kg (約6獨立小包，賣場原牌價 $215/kg)",
        "total_weight_grams": 2700,
        "note": "好市多經典生鮮台灣冷藏雞清胸肉，今購百科門市實拍原牌價為每公斤 $215（換算每 100g 為 NT$ 21.5，每台斤約 NT$ 129）。"
    },
    {
        "id": "chicken-08",
        "code": "149292",
        "name": "台灣益活雞冷藏去骨清雞腿",
        "filename": "chicken-08.jpg",
        "costco_img": "https://www.costco.com.tw/medias/sys_master/images/h2d/h19/363704930762782.jpg",
        "price_per_kg": 399.0,
        "original_price": 1077, # 2.7kg * 399
        "package_spec": "2.7kg (多小袋入，賣場原牌價 $399/kg)",
        "total_weight_grams": 2700,
        "note": "大成益活雞冷藏去骨清雞腿，熟成無腥味，今購百科門市實拍原牌價為每公斤 $399（換算每 100g 為 NT$ 39.9）。"
    },
    {
        "id": "chicken-09",
        "code": "150408",
        "name": "台灣土雞去骨清雞腿",
        "filename": "chicken-09.jpg",
        "costco_img": "https://www.costco.com.tw/medias/sys_master/images/h66/hb7/363704932204574.jpg",
        "price_per_kg": 479.0,
        "original_price": 485,
        "package_spec": "1.013kg (盒裝，賣場原牌價 $479/kg)",
        "total_weight_grams": 1013,
        "note": "台灣土雞王去骨清雞腿，肉質緊實Q彈，今購百科門市包裝貼紙實拍原牌價為每公斤 $479（換算每 100g 為 NT$ 47.9）。"
    },
    {
        "id": "chicken-10",
        "code": "159889",
        "name": "台灣羅勒去骨清雞腿 (調理包)",
        "filename": "chicken-10.jpg",
        "costco_img": "https://www.costco.com.tw/medias/sys_master/images/h24/h55/417161993355294.jpg",
        "price_per_kg": 299.0,
        "original_price": 688,
        "package_spec": "2.3kg (3聯包，賣場原牌價約 $299/kg)",
        "total_weight_grams": 2300,
        "note": "大成羅勒去骨清雞腿調理包，義式香草青醬醃漬，今購百科門市實拍原牌價為每公斤 $299（換算每 100g 為 NT$ 29.9）。"
    }
]

print("=== Downloading Official Costco Clean Studio Photos ===")
for item in official_items:
    fname = item["filename"]
    p_dest = os.path.join(PUB_IMG, fname)
    d_dest = os.path.join(DIST_IMG, fname)
    url = item["costco_img"]
    print(f"Downloading official photo for #{item['code']} -> {fname}...")
    cmd = f'curl.exe -s -L -k "{url}" -o "{p_dest}"'
    res = subprocess.run(cmd, shell=True)
    if res.returncode == 0 and os.path.exists(p_dest) and os.path.getsize(p_dest) > 1000:
        shutil.copy2(p_dest, d_dest)
        print(f"  [OK] Saved official studio photo ({os.path.getsize(p_dest)} bytes)")
    else:
        print(f"  [WARN] Download fallback check")

# 2. Update SQLite database: Set pure original price, discount = 0 (no past discount info applied as current)
print("\n=== Updating SQLite Database with Pure Original Prices (No Past Expired Discounts) ===")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

for item in official_items:
    pid = item["id"]
    cursor.execute("""
    UPDATE products SET
        name = ?,
        original_price = ?,
        discount_amount = 0,
        discount_end_date = NULL,
        price_per_kg = ?,
        package_spec = ?,
        total_weight_grams = ?,
        tag_type = 'everyday_value',
        historical_benchmark = 'standard',
        storage_type = 'cold',
        pricing_type = 'by_weight',
        price_source = 'warehouse_only',
        verified_source = '今購百科 賣場現場實拍原牌價',
        is_estimated_price = 0,
        price_origin = 'store_tag',
        note = ?,
        image_url = ?,
        local_image_path = ?,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = ? OR costco_item_number = ?;
    """, (
        item["name"],
        item["original_price"],
        item["price_per_kg"],
        item["package_spec"],
        item["total_weight_grams"],
        item["note"],
        item["costco_img"],
        f"/images/products/{item['filename']}",
        pid,
        item["code"]
    ))
    print(f"  [DB RESTORED] #{item['code']} {item['name']}: 原價 NT${item['price_per_kg']}/kg -> 每100g NT${round(item['price_per_kg']/10, 2)} (無過期特價干擾)")

conn.commit()
conn.close()

# 3. Export to frontend
from scripts.import_all_costco_food import export_all_to_frontend
export_all_to_frontend()
print("=== All Restored Cleanly to Official Studio Photos and Pure Original Prices! ===")
