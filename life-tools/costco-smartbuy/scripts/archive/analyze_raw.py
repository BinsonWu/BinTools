import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/Binson/Mytools/Python/SideProject/Costco/scripts/all_food_raw.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f"Total products: {len(products)}")

with_price = 0
without_price = 0
with_images = 0
with_discount = 0
sample_chicken = []

for p in products:
    name = p.get('name', '')
    code = p.get('code', '')
    price = p.get('price', {}).get('value')
    base_price = p.get('basePrice', {}).get('value')
    coupon = p.get('couponDiscount', {})
    images = p.get('images', [])

    if price is not None:
        with_price += 1
    else:
        without_price += 1

    if images:
        with_images += 1

    if coupon and coupon.get('discountValue', 0) > 0:
        with_discount += 1

    if '去骨清雞腿' in name or '清雞腿' in name or code == '133600':
        sample_chicken.append((code, name, price, base_price, coupon, images[0] if images else None))

print(f"Products with price: {with_price}")
print(f"Products without price: {without_price}")
print(f"Products with images: {with_images}")
print(f"Products with active coupon discount: {with_discount}")

print("\nChicken leg items found:")
for code, name, price, base_price, coupon, img in sample_chicken:
    print(f"  #{code}: {name}")
    print(f"     Price: ${price}, Base: ${base_price}, Coupon: {coupon}")
    print(f"     Image: {img.get('url') if img else None}")
