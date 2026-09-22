import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/Binson/Mytools/Python/SideProject/Costco/scripts/all_food_raw.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

def parse_weight(title, desc=""):
    text = title + " " + desc[:3000]
    # Check for kg with count: e.g. 2.5公斤 X 2入, 2.7 kg x 5
    m = re.search(r'([\d\.]+)\s*(?:kg|KG|公斤)\s*[xX*入包袋盒瓶]\s*(\d+)', text)
    if m:
        return int(float(m.group(1)) * 1000 * int(m.group(2))), 'g', f"{m.group(1)}kg x {m.group(2)}"
    
    # Check for grams with count: e.g. 700公克 X 2入, 840g x 2
    m = re.search(r'(\d+)\s*(?:g|G|公克)\s*[xX*入包袋盒瓶]\s*(\d+)', text)
    if m:
        return int(m.group(1)) * int(m.group(2)), 'g', f"{m.group(1)}g x {m.group(2)}"
    
    # Check for Liters with count: e.g. 1公升 X 6入, 1.8L x 2
    m = re.search(r'([\d\.]+)\s*(?:L|l|公升)\s*[xX*入包袋盒瓶]\s*(\d+)', text)
    if m:
        return int(float(m.group(1)) * 1000 * int(m.group(2))), 'ml', f"{m.group(1)}L x {m.group(2)}"
    
    # Check for ml with count: e.g. 340毫升 X 12入, 250ml x 24
    m = re.search(r'(\d+)\s*(?:ml|ML|毫升)\s*[xX*入包袋盒瓶]\s*(\d+)', text)
    if m:
        return int(m.group(1)) * int(m.group(2)), 'ml', f"{m.group(1)}ml x {m.group(2)}"
    
    # Check for single kg: e.g. 1.3公斤, 5公斤, 2.5kg
    m = re.search(r'([\d\.]+)\s*(?:kg|KG|公斤)', text)
    if m:
        return int(float(m.group(1)) * 1000), 'g', f"{m.group(1)}kg"
    
    # Check for single Liter: e.g. 1公升, 1.8L
    m = re.search(r'([\d\.]+)\s*(?:L|l|公升)', text)
    if m:
        return int(float(m.group(1)) * 1000), 'ml', f"{m.group(1)}L"
    
    # Check for single grams: e.g. 800公克, 600g
    m = re.search(r'(\d+)\s*(?:g|G|公克)', text)
    if m:
        return int(m.group(1)), 'g', f"{m.group(1)}g"
    
    # Check for single ml: e.g. 500毫升, 750ml
    m = re.search(r'(\d+)\s*(?:ml|ML|毫升)', text)
    if m:
        return int(m.group(1)), 'ml', f"{m.group(1)}ml"
    
    # Check for lbs: e.g. 2磅 / 908公克
    m = re.search(r'([\d\.]+)\s*(?:磅|lbs|lb|LBs)', text)
    if m:
        return int(float(m.group(1)) * 453.6), 'g', f"{m.group(1)}磅"

    # Default to 1000g
    return 1000, 'g', '標準包裝'

success = 0
examples = []

for p in products:
    name = p.get('name', '')
    desc = p.get('description', '')
    weight, unit, spec = parse_weight(name, desc)
    price = p.get('price', {}).get('value')
    if weight != 1000 or '1000' in name or '1公斤' in name or '1kg' in name:
        success += 1
    if any(k in name for k in ['雞腿', '橄欖油', '牛肉', '鮭魚', '咖啡', '燕麥', '洋芋片']):
        examples.append((name, spec, weight, unit, price, round(price / (weight/100), 1) if price and weight else None))

print(f"Weight parsed successfully for {success}/{len(products)} products")
print("\nSample parsed items:")
for name, spec, weight, unit, price, per100 in examples[:15]:
    print(f"  {name[:35]:<35} | {spec:<15} | {weight}{unit:<2} | ${price} -> ${per100}/{100}{unit}")
