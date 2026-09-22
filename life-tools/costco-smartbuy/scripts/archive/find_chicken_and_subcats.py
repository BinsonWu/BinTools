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

# Check search for '雞腿'
for term in ['雞腿', '去骨', '清雞腿', '大成']:
    s_url = f'https://www.costco.com.tw/search?text={urllib.parse.quote(term)}'
    html = fetch_url(s_url)
    # find links with name
    links = re.findall(r'href=[\'"]([^\'"]+/p/(\d+))[\'"]', html)
    print(f"Search '{term}': {len(links)} links found")
    unique_links = list(dict.fromkeys(links))
    for link, sku in unique_links[:10]:
        # extract title
        print(f"  #{sku}: {link}")

# Let's inspect subcategories under Food-Dining:
html_c8 = fetch_url('https://www.costco.com.tw/Food-Dining/c/8')
# Find all <a href="...">
all_links = set(re.findall(r'href=[\'"](/Food-Dining/[^\'"#\?]+)[\'"]', html_c8))
print(f"\nAll /Food-Dining/ sub-paths in c/8: {len(all_links)}")
for l in sorted(all_links):
    print(" ", l)
