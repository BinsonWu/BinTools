import urllib.request
import ssl
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl._create_unverified_context()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept-Language': 'zh-TW,zh;q=0.9',
}

test_skus = ['118583', '110478', '111452', '112390', '87754', '149292']

for sku in test_skus:
    url = f"https://www.daybuy.tw/?s={sku}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            # Look for costco post links: e.g. https://www.daybuy.tw/costco/(\d+)/
            links = re.findall(r'href=[\'"](https://www\.daybuy\.tw/costco/\d+/)[\'"]', html)
            unique_links = list(dict.fromkeys(links))
            print(f"Search SKU #{sku}: found {len(unique_links)} Daybuy post links: {unique_links[:2]}")
    except Exception as e:
        print(f"Search SKU #{sku} error: {e}")
