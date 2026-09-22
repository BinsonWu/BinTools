"""
Update Uncertain Costco Prices from Daybuy.tw Store Price Tags & Package Photos.
"""

import os
import sys
import sqlite3
import shutil
import json

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
DB_PATH = os.path.join(PROJECT_ROOT, "costco_products.db")
PUB_IMG = os.path.join(PROJECT_ROOT, "public", "images", "products")
DIST_IMG = os.path.join(PROJECT_ROOT, "dist", "images", "products")
DAYBUY_IMG = os.path.join(PROJECT_ROOT, "scripts", "daybuy_img")

os.makedirs(PUB_IMG, exist_ok=True)
os.makedirs(DIST_IMG, exist_ok=True)

def copy_img(src_name, target_name):
    src = os.path.join(DAYBUY_IMG, src_name)
    if os.path.exists(src):
        p_dest = os.path.join(PUB_IMG, target_name)
        d_dest = os.path.join(DIST_IMG, target_name)
        shutil.copy2(src, p_dest)
        shutil.copy2(src, d_dest)
        print(f"  [IMG OK] Copied {src_name} -> {target_name}")
        return f"/images/products/{target_name}"
    return None

def update_prices():
    print("=== Updating Uncertain Prices using Daybuy Store Photos ===")
    
    # 1. Copy images
    img_118583 = copy_img("118583_0.jpg", "chicken-02.jpg") or "/images/products/chicken-02.jpg"
    img_149292 = copy_img("149292_0.jpg", "chicken-08.jpg") or "/images/products/chicken-08.jpg"
    img_150408 = copy_img("150408_native_chicken_1.jpg", "chicken-09.jpg") or "/images/products/chicken-09.jpg"
    img_159889 = copy_img("159889_basil_chicken_0.jpg", "chicken-10.jpg") or "/images/products/chicken-10.jpg"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    items_to_update = [
        {
            "id": "chicken-02",
            "name": "冷藏台灣去骨清雞腿真空包",
            "category": "chicken",
            "sub_category": "冷藏生鮮/去骨雞腿",
            "costco_item_number": "118583",
            "price_per_kg": 245.0,
            "original_price": 674,
            "discount_amount": 138, # 2.75kg * $50/kg discount = $138, 特價 $536 (即 $195/kg)
            "discount_end_date": "2025-12-21",
            "package_spec": "2.75kg (單包約6小包，賣場牌價 $245/kg)",
            "total_weight_grams": 2750,
            "unit_type": "g",
            "tag_type": "weekly_sale",
            "historical_benchmark": "historical_low",
            "storage_type": "cold",
            "pricing_type": "by_weight",
            "price_source": "warehouse_only",
            "verified_source": "今購百科 賣場現場標價牌實拍 (#81651)",
            "historical_range_min": 19.5,
            "historical_range_max": 24.5,
            "is_estimated_price": 0,
            "price_origin": "store_tag",
            "note": "好市多門市冷藏去骨清雞腿真空包 (#118583)，今購百科門市實拍牌價為每公斤 $245（每 100g 約 NT$ 24.5）！現場檔期現折 $50/kg，特價每公斤只要 $195（每 100g NT$ 19.5），超人氣生鮮原肉！",
            "local_image_path": img_118583,
            "image_url": "https://static.daybuy.tw/wp-content/uploads/2025/12/LINE_ALBUM_第4檔_251212_17-600x800.jpg"
        },
        {
            "id": "chicken-08",
            "name": "台灣益活雞冷藏去骨清雞腿",
            "category": "chicken",
            "sub_category": "冷藏生鮮/益活雞",
            "costco_item_number": "149292",
            "price_per_kg": 399.0,
            "original_price": 1077,
            "discount_amount": 216, # 2.7kg * $80/kg = $216, 特價 $861 (即 $319/kg)
            "discount_end_date": "2026-04-12",
            "package_spec": "2.7kg (多小袋入，牌價 $399/kg)",
            "total_weight_grams": 2700,
            "unit_type": "g",
            "tag_type": "weekly_sale",
            "historical_benchmark": "historical_low",
            "storage_type": "cold",
            "pricing_type": "by_weight",
            "price_source": "warehouse_only",
            "verified_source": "今購百科 賣場現場標價牌實拍 (#163365)",
            "historical_range_min": 31.9,
            "historical_range_max": 39.9,
            "is_estimated_price": 0,
            "price_origin": "store_tag",
            "note": "大成益活雞冷藏去骨清雞腿 (#149292)，無腥味鮮甜肉質，今購百科門市實拍標價牌為每公斤 $399（每 100g 約 NT$ 39.9），活動特價每公斤折 $80，只要 $319/kg（每 100g NT$ 31.9）！",
            "local_image_path": img_149292,
            "image_url": "https://static.daybuy.tw/wp-content/uploads/2024/12/LINE_ALBUM_第2波_260326_1-800x600.jpg"
        },
        {
            "id": "chicken-09",
            "name": "台灣土雞去骨清雞腿",
            "category": "chicken",
            "sub_category": "冷藏生鮮/土雞腿",
            "costco_item_number": "150408",
            "price_per_kg": 479.0,
            "original_price": 485,
            "discount_amount": 0,
            "discount_end_date": None,
            "package_spec": "1.013kg (盒裝，牌價 $479/kg)",
            "total_weight_grams": 1013,
            "unit_type": "g",
            "tag_type": "everyday_value",
            "historical_benchmark": "standard",
            "storage_type": "cold",
            "pricing_type": "by_weight",
            "price_source": "warehouse_only",
            "verified_source": "今購百科 門市包裝標籤實拍 (#174352)",
            "historical_range_min": 45.0,
            "historical_range_max": 51.0,
            "is_estimated_price": 0,
            "price_origin": "store_tag",
            "note": "台灣土雞王去骨清雞腿 (#150408)，肉質Q彈緊實，今購百科門市肉品盒實拍牌價為每公斤 $479（每 100g 約 NT$ 47.9）。",
            "local_image_path": img_150408,
            "image_url": "https://static.daybuy.tw/wp-content/uploads/2025/02/IMG_5839-800x600.jpeg"
        },
        {
            "id": "chicken-10",
            "name": "台灣羅勒去骨清雞腿 (調理包)",
            "category": "chicken",
            "sub_category": "冷藏調理/調味雞腿",
            "costco_item_number": "159889",
            "price_per_kg": 299.0,
            "original_price": 688,
            "discount_amount": 0,
            "discount_end_date": None,
            "package_spec": "2.3kg (3聯包，牌價約 $299/kg)",
            "total_weight_grams": 2300,
            "unit_type": "g",
            "tag_type": "none",
            "historical_benchmark": "standard",
            "storage_type": "cold",
            "pricing_type": "by_weight",
            "price_source": "warehouse_only",
            "verified_source": "今購百科 門市包裝標籤實拍 (#235635)",
            "historical_range_min": 28.5,
            "historical_range_max": 31.5,
            "is_estimated_price": 0,
            "price_origin": "store_tag",
            "note": "大成羅勒去骨清雞腿 (#159889)，義式香草青醬醃漬，氣炸煎烤多汁開胃，今購百科門市包裝標籤實拍牌價約 $299/kg（每 100g 約 NT$ 29.9）。",
            "local_image_path": img_159889,
            "image_url": "https://static.daybuy.tw/wp-content/uploads/2026/02/IMG_0261-800x600.jpeg"
        }
    ]

    for it in items_to_update:
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
            local_image_path=excluded.local_image_path,
            pricing_type=excluded.pricing_type,
            price_per_kg=excluded.price_per_kg,
            price_source=excluded.price_source,
            costco_item_number=excluded.costco_item_number,
            verified_source=excluded.verified_source,
            historical_range_min=excluded.historical_range_min,
            historical_range_max=excluded.historical_range_max,
            is_estimated_price=excluded.is_estimated_price,
            price_origin=excluded.price_origin,
            updated_at=CURRENT_TIMESTAMP;
        """, (
            it["id"], it["name"], it["category"], it["sub_category"], it["original_price"],
            it["discount_amount"], it["discount_end_date"], it["package_spec"],
            it["total_weight_grams"], it["unit_type"], it["tag_type"], it["historical_benchmark"],
            it["storage_type"], it["note"], it["image_url"], it["local_image_path"],
            it["pricing_type"], it["price_per_kg"], it["price_source"], it["costco_item_number"],
            it["verified_source"], it["historical_range_min"], it["historical_range_max"],
            it["is_estimated_price"], it["price_origin"]
        ))
        print(f"  [DB UPDATED] #{it['costco_item_number']}: {it['name']} -> ${it['price_per_kg']}/kg (NT${round(it['price_per_kg']/10, 2)}/100g)")

    conn.commit()
    conn.close()

    # Now trigger export to frontend
    from scripts.import_all_costco_food import export_all_to_frontend
    export_all_to_frontend()
    print("=== Update Complete! ===")

if __name__ == "__main__":
    update_prices()
