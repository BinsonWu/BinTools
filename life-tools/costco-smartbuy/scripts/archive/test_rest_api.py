import sys
import urllib.request
import ssl
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl._create_unverified_context()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept-Language': 'zh-TW,zh;q=0.9',
}

# Let's search costco api or website for CP / 卜蜂
for kw in ['卜蜂', '雞腿', '去骨清雞腿', '去骨']:
    url = f"https://www.costco.com.tw/rest/v2/taiwan/products/search?query={urllib.parse.quote(kw)}&pageSize=20"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"REST API query '{kw}': total {data.get('pagination', {}).get('totalResults')} results")
            for p in data.get('products', []):
                print(f"  #{p.get('code')}: {p.get('name')} - NT${p.get('price', {}).get('value')}")
    except Exception as e:
        print(f"REST API error for {kw}: {e}")
