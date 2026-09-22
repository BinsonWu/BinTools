import urllib.request
import ssl
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
ctx = ssl._create_unverified_context()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept-Language': 'zh-TW,zh;q=0.9',
}

url = 'https://www.costco.com.tw/rest/v2/taiwan/products/search?fields=FULL&query=:relevance:category:WH08&pageSize=20'
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        total = data.get('pagination', {}).get('totalResults')
        print(f"Total Results in WH08: {total}")
        for p in data.get('products', []):
            code = p.get('code')
            name = p.get('name')
            price = p.get('price')
            imgs = p.get('images', [])
            first_img = imgs[0].get('url') if imgs else None
            print(f"#{code}: {name} | price={price} | img={first_img}")
except Exception as e:
    print(f"Error: {e}")
