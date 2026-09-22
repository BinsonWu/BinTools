import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('scripts/all_food_raw.json', 'r', encoding='utf-8') as f:
    raw = json.load(f)

for code in ['118583', '149292', '150408', '159889', '110478']:
    matches = [p for p in raw if str(p.get('code')) == code]
    if matches:
        p = matches[0]
        print(f"#{code}: {p.get('name')}")
        imgs = p.get('images', [])
        for img in imgs:
            if img.get('format') == 'product':
                print(f"   Official CDN: https://www.costco.com.tw{img.get('url')}")
    else:
        print(f"#{code} not in raw")
