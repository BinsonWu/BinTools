import sys
import urllib.request
import ssl
import json
import time

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl._create_unverified_context()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept-Language': 'zh-TW,zh;q=0.9',
}

all_products = []
start_time = time.time()

for page in range(13):
    url = f"https://www.costco.com.tw/rest/v2/taiwan/products/search?query=:relevance:allCategories:8&pageSize=100&currentPage={page}&fields=FULL"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            prods = data.get('products', [])
            all_products.extend(prods)
            print(f"Page {page+1}/13: fetched {len(prods)} products (total: {len(all_products)})")
    except Exception as e:
        print(f"Page {page+1} error: {e}")

elapsed = time.time() - start_time
print(f"Done! Fetched {len(all_products)} products in {elapsed:.2f} seconds.")

# Save to a temporary json file for inspection
with open('scripts/all_food_raw.json', 'w', encoding='utf-8') as f:
    json.dump(all_products, f, ensure_ascii=False, indent=2)
print("Saved raw products to scripts/all_food_raw.json")
