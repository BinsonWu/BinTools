import urllib.request
import ssl
import json

ctx = ssl._create_unverified_context()
headers = {'User-Agent': 'Mozilla/5.0'}
for cat in ['8', '901', '902', '907', '908']:
    url = f"https://www.costco.com.tw/rest/v2/taiwan/products/search?query=:relevance:allCategories:{cat}&pageSize=1"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        d = json.loads(resp.read().decode('utf-8'))
        print(f"allCategories:{cat} -> {d.get('pagination', {}).get('totalResults')} items")
