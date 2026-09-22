import sys
import urllib.request
import ssl
import json

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl._create_unverified_context()
headers = {'User-Agent': 'Mozilla/5.0'}

# Search all pages of allCategories:8
total_chicken = []
for page in range(13):
    url = f"https://www.costco.com.tw/rest/v2/taiwan/products/search?query=:relevance:allCategories:8&pageSize=100&currentPage={page}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        products = data.get('products', [])
        for p in products:
            name = p.get('name', '')
            if '雞腿' in name or '雞' in name:
                total_chicken.append((p.get('code'), name, p.get('price', {}).get('value'), p.get('basePrice', {}).get('value')))

print(f"Found {len(total_chicken)} chicken items in allCategories:8:")
for code, name, price, base_price in total_chicken:
    print(f"  #{code}: {name} -> Sale: ${price}, Base: ${base_price}")
