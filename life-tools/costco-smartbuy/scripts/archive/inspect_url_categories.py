import json
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/Binson/Mytools/Python/SideProject/Costco/scripts/all_food_raw.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

url_prefixes = {}
for p in products:
    url = p.get('url', '')
    # Extract path segments before the product name
    m = re.match(r'/(?:Food-Dining/)?([^/]+)(?:/([^/]+))?', url)
    if m:
        prefix = f"{m.group(1)}/{m.group(2) or ''}"
        url_prefixes[prefix] = url_prefixes.get(prefix, 0) + 1

print(f"URL Categories Distribution ({len(url_prefixes)} groups):")
for prefix, count in sorted(url_prefixes.items(), key=lambda x: -x[1]):
    print(f"  {prefix}: {count}")
