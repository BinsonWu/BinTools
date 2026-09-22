import sys
import urllib.request
import ssl
import json

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl._create_unverified_context()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept-Language': 'zh-TW,zh;q=0.9',
}

test_queries = [
    ":relevance:category:8",
    ":relevance:category:901",
    ":relevance:category:902",
    ":relevance:category:907",
    ":relevance:category:908",
    ":relevance:allCategories:8",
    ":relevance:allCategories:908",
]

for q in test_queries:
    url = f"https://www.costco.com.tw/rest/v2/taiwan/products/search?query={urllib.parse.quote(q)}&pageSize=5"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            total = data.get('pagination', {}).get('totalResults')
            facets = [f.get('name') for f in data.get('facets', [])]
            print(f"Query '{q}': total {total} results! Facets: {facets[:4]}")
            for p in data.get('products', [])[:2]:
                print(f"  #{p.get('code')}: {p.get('name')}")
    except Exception as e:
        print(f"Query '{q}' error: {e}")
