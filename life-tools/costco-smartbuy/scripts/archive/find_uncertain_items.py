import sqlite3
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('costco_products.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Find items in DB that are warehouse_only or estimated or by_weight
cursor.execute("""
SELECT id, costco_item_number, name, category, pricing_type, price_per_kg, original_price, price_source, verified_source, is_estimated_price
FROM products
WHERE pricing_type = 'by_weight' OR price_source = 'warehouse_only' OR is_estimated_price = 1 OR costco_item_number IN ('118583', '110478', '111452', '112390', '87754', '149292', '150408', '163878', '159889')
""")
rows = cursor.fetchall()

print(f"Items in DB with warehouse/by_weight/estimated prices: {len(rows)}")
for r in rows:
    print(f"  #{r['costco_item_number']}: {r['name']} | perKg: ${r['price_per_kg']} | Orig: ${r['original_price']} | Source: {r['price_source']} | Ver: {r['verified_source']}")

# Also check raw_items that had price == None in scripts/all_food_raw.json
with open('scripts/all_food_raw.json', 'r', encoding='utf-8') as f:
    raw = json.load(f)

unpriced = [p for p in raw if p.get('price', {}).get('value') is None and p.get('basePrice', {}).get('value') is None]
print(f"\nTotal unpriced raw items from Costco API: {len(unpriced)}")
for p in unpriced[:15]:
    print(f"  #{p.get('code')}: {p.get('name')}")
