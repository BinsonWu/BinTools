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

url = "https://www.costco.com.tw/rest/v2/taiwan/products/search?query=" + urllib.parse.quote(":relevance:allCategories:8") + "&pageSize=3&fields=FULL"
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print("Keys:", data.keys())
        prod = data.get('products', [])[0]
        print("Product fields:", prod.keys())
        print(json.dumps(prod, indent=2, ensure_ascii=False))
except Exception as e:
    print("Error:", e)
