import sys
import urllib.request
import ssl
import re
import json

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

# 1. Inspect All-Food-Dining /c/918 or Frozen-Fresh-Food /c/908
urls = [
    'https://www.costco.com.tw/Food-Dining/Frozen-Fresh-Food/c/908',
    'https://www.costco.com.tw/Food-Dining/All-Food-Dining/c/918',
    'https://www.costco.com.tw/Food-Dining/All-Food-Dining/c/918?pageSize=96&page=0',
]

for u in urls:
    try:
        html = fetch_url(u)
        prod_links = list(dict.fromkeys(re.findall(r'href=[\'"]([^\'"]+/p/\d+)[\'"]', html)))
        print(f"URL: {u} -> HTML len: {len(html)}, Products: {len(prod_links)}")
        if prod_links:
            print("  First 3:", prod_links[:3])
        # Look for subcategories
        cat_links = list(dict.fromkeys(re.findall(r'href=[\'"](/Food-Dining/[^\'"]+/c/\d+)[\'"]', html)))
        print(f"  Category links found: {len(cat_links)}")
        for c in cat_links[:5]:
            print("    ", c)
    except Exception as e:
        print(f"Error {u}: {e}")

# Search for "去骨清雞腿" specifically
search_url = 'https://www.costco.com.tw/search?text=' + urllib.parse.quote('去骨清雞腿')
try:
    s_html = fetch_url(search_url)
    prod_links = list(dict.fromkeys(re.findall(r'href=[\'"]([^\'"]+/p/\d+)[\'"]', s_html)))
    print(f"\nSearch '去骨清雞腿': found {len(prod_links)} products")
    for p in prod_links:
        print(" ", p)
except Exception as e:
    print("Search error:", e)

