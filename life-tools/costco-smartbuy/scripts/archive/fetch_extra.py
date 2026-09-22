import urllib.request
import ssl
import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl._create_unverified_context()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
}

skus = ["68523", "117869", "86420", "124981", "171168", "92144", "115982"]
results = {}

for sku in skus:
    url = f"https://www.costco.com.tw/p/{sku}"
    print(f"Fetching SKU #{sku}...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=12) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            
            og_img = re.search(r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)["\']', html)
            if not og_img:
                og_img = re.search(r'content=["\']([^"\']+)["\']\s+property=["\']og:image["\']', html)
            
            og_title = re.search(r'<meta\s+property=["\']og:title["\']\s+content=["\']([^"\']+)["\']', html)
            if not og_title:
                og_title = re.search(r'<title>([^<]+)</title>', html)
                
            price_match = re.search(r'"price":\s*"([\d\.]+)"', html)
            
            img_url = og_img.group(1) if og_img else None
            title = og_title.group(1).replace(' | Costco 好市多', '').strip() if og_title else None
            price = price_match.group(1) if price_match else None
            
            results[sku] = {
                "sku": sku,
                "title": title,
                "img_url": img_url,
                "price": price,
                "url": url
            }
            print(f"  -> Title: {title}")
            print(f"  -> Image: {img_url}")
            print(f"  -> Price: {price}")
    except Exception as e:
        print(f"  -> Error for #{sku}: {e}")

with open(r'scripts/fetched_extra_items.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("Finished extra items")
