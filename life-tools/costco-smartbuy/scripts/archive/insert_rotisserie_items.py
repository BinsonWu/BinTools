import sqlite3
import json
import os

DB_PATH = 'costco_products.db'
SRC_JSON = 'src/data/products.json'
PUB_JSON = 'public/data/products.json'
MOCK_TS = 'src/data/mockProducts.ts'

items_to_add = [
    {
        'id': 'costco-112179',
        'name': '科克蘭 美式大烤雞 1450公克',
        'category': 'chicken',
        'subCategory': '熟食即食部',
        'pricingType': 'fixed_package',
        'originalPrice': 189,
        'discountAmount': 0,
        'discountEndDate': None,
        'packageSpec': '1隻 (約1450g)',
        'totalWeightInGrams': 1450,
        'unitType': 'g',
        'tagType': 'everyday_value',
        'historicalBenchmark': 'historical_low',
        'storageType': 'room',
        'note': '好市多熟食部靈魂全熟烤雞，全場熟肉最高CP值首選！',
        'imageUrl': 'https://www.costco.com.tw/medias/sys_master/images/hf3/h97/132201737977886.jpg',
        'localImage': '/images/products/chicken-rotisserie-whole.jpg',
        'priceSource': 'warehouse_only',
        'costcoItemNumber': '112179',
        'verifiedSource': '好市多賣場熟食部標牌價 NT$189',
        'priceOrigin': 'store_tag',
        'isEstimatedPrice': False
    },
    {
        'id': 'costco-458155',
        'name': '科克蘭 烤雞大腿4入 825公克',
        'category': 'chicken',
        'subCategory': '熟食即食部',
        'pricingType': 'fixed_package',
        'originalPrice': 198,
        'discountAmount': 0,
        'discountEndDate': None,
        'packageSpec': '4入 (約825g)',
        'totalWeightInGrams': 825,
        'unitType': 'g',
        'tagType': 'everyday_value',
        'historicalBenchmark': 'standard',
        'storageType': 'room',
        'note': '特調醃烤醬醃製黃金大烤雞腿，熟食部熱賣限定。',
        'imageUrl': 'https://www.costco.com.tw/medias/sys_master/images/h73/hb7/12522596040734.jpg',
        'localImage': '/images/products/chicken-rotisserie-thigh.jpg',
        'priceSource': 'warehouse_only',
        'costcoItemNumber': '458155',
        'verifiedSource': '好市多賣場熟食部標牌價 NT$198',
        'priceOrigin': 'store_tag',
        'isEstimatedPrice': False
    }
]

# 1. Update SQLite
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

for item in items_to_add:
    c.execute('''
        INSERT OR REPLACE INTO products (
            id, name, category, sub_category, original_price, discount_amount,
            discount_end_date, package_spec, total_weight_grams, unit_type,
            tag_type, historical_benchmark, storage_type, note, image_url,
            local_image_path, pricing_type, price_source, costco_item_number,
            verified_source, price_origin, is_estimated_price, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (
        item['id'], item['name'], item['category'], item['subCategory'],
        item['originalPrice'], item['discountAmount'], item['discountEndDate'],
        item['packageSpec'], item['totalWeightInGrams'], item['unitType'],
        item['tagType'], item['historicalBenchmark'], item['storageType'],
        item['note'], item['imageUrl'], item['localImage'],
        item['pricingType'], item['priceSource'], item['costcoItemNumber'],
        item['verifiedSource'], item['priceOrigin'], 1 if item['isEstimatedPrice'] else 0
    ))

conn.commit()

# Query all products from SQLite
c.execute('''
    SELECT id, name, category, sub_category, pricing_type, price_per_kg,
           original_price, discount_amount, discount_end_date, package_spec,
           total_weight_grams, unit_type, tag_type, historical_benchmark,
           storage_type, note, image_url, local_image_path, price_source,
           costco_item_number, verified_source, is_estimated_price, price_origin
    FROM products
    ORDER BY category, name
''')

all_products = []
for row in c.fetchall():
    all_products.append({
        'id': row[0],
        'name': row[1],
        'category': row[2],
        'subCategory': row[3],
        'pricingType': row[4],
        'pricePerKg': row[5],
        'originalPrice': row[6],
        'discountAmount': row[7],
        'discountEndDate': row[8],
        'packageSpec': row[9],
        'totalWeightInGrams': row[10],
        'unitType': row[11],
        'tagType': row[12],
        'historicalBenchmark': row[13],
        'storageType': row[14],
        'note': row[15],
        'imageUrl': row[16],
        'localImage': row[17],
        'priceSource': row[18],
        'costcoItemNumber': row[19],
        'verifiedSource': row[20],
        'isEstimatedPrice': bool(row[21]),
        'priceOrigin': row[22]
    })

conn.close()

print(f'Total products in database: {len(all_products)}')

# 2. Write to products.json
with open(SRC_JSON, 'w', encoding='utf-8') as f:
    json.dump(all_products, f, ensure_ascii=False, indent=2)

with open(PUB_JSON, 'w', encoding='utf-8') as f:
    json.dump(all_products, f, ensure_ascii=False, indent=2)

print('Updated JSON files successfully!')
