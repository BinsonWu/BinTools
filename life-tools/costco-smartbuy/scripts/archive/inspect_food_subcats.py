import sys
import urllib.request
import ssl
import re

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl._create_unverified_context()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept-Language': 'zh-TW,zh;q=0.9',
}

def fetch_url(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
        return resp.read().decode('utf-8', errors='ignore')

main_cats = [
    ('Frozen-Fresh-Food', 'https://www.costco.com.tw/Food-Dining/Frozen-Fresh-Food/c/908'),
    ('Groceries', 'https://www.costco.com.tw/Food-Dining/Groceries/c/907'),
    ('Snacks', 'https://www.costco.com.tw/Food-Dining/Snacks/c/902'),
    ('Drinks', 'https://www.costco.com.tw/Food-Dining/Drinks/c/901'),
]

for name, url in main_cats:
    html = fetch_url(url)
    print(f"\n=== {name} ({url}) ===")
    sub_cats = set(re.findall(r'href=[\'"](/Food-Dining/[^\'"#\?]+/c/\d+)[\'"]', html))
    print(f"Subcategories ({len(sub_cats)}):")
    for s in sorted(sub_cats):
        print("  ", s)
    prods = list(dict.fromkeys(re.findall(r'href=[\'"]([^\'"]+/p/(\d+))[\'"]', html)))
    print(f"Direct products on page: {len(prods)}")
    for link, sku in prods[:5]:
        print(f"   #{sku}: {link}")
