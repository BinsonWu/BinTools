import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('costco_products.db')
cursor = conn.cursor()
for code in ['133600', '1236329', '133321', '484596', '110478']:
    cursor.execute('SELECT costco_item_number, name, original_price, discount_amount, total_weight_grams, unit_type, package_spec, image_url FROM products WHERE costco_item_number=?', (code,))
    row = cursor.fetchone()
    if row:
        unit = row[5] or 'g'
        weight = row[4]
        price = row[2]
        per100 = round(price / (weight / 100), 2) if weight else 'N/A'
        print(f"#{row[0]}: {row[1]}")
        print(f"   總價: ${price} (折讓: ${row[3]}) | 規格: {weight}{unit} ({row[6]}) | 每100{unit}: NT$ {per100}")
        print(f"   圖片: {row[7]}")
    else:
        print(f"#{code} not found!")
