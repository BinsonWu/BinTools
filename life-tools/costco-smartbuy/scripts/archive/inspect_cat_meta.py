import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/Binson/Mytools/Python/SideProject/Costco/scripts/all_food_raw.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

for p in products[:5]:
    print("Name:", p.get('name'))
    print("URL:", p.get('url'))
    print("categories:", p.get('categories'))
    print("classification:", p.get('classifications'))
    print("---")
