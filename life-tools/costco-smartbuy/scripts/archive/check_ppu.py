import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/Binson/Mytools/Python/SideProject/Costco/scripts/all_food_raw.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

has_ppu = 0
no_ppu = 0
ppu_types = {}

for p in products:
    ppu = p.get('pricePerUnit')
    ut = p.get('unitType')
    if ppu and ppu.get('value'):
        has_ppu += 1
        ppu_types[ut] = ppu_types.get(ut, 0) + 1
    else:
        no_ppu += 1

print(f"Products with official pricePerUnit: {has_ppu} / {len(products)}")
print(f"Products without official pricePerUnit: {no_ppu}")
print("Price per unit types distribution:")
for ut, count in sorted(ppu_types.items(), key=lambda x: -x[1]):
    print(f"  '{ut}': {count}")
