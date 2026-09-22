import urllib.request
import ssl
import re
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl._create_unverified_context()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept-Language': 'zh-TW,zh;q=0.9',
}

def get_daybuy_post_for_sku(sku):
    search_url = f"https://www.daybuy.tw/?s={sku}"
    req = urllib.request.Request(search_url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            links = re.findall(r'href=[\'"](https://www\.daybuy\.tw/costco/\d+/)[\'"]', html)
            return list(dict.fromkeys(links))
    except Exception as e:
        print(f"Error searching {sku}: {e}")
        return []

def inspect_daybuy_page(url):
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            title = re.search(r'<title>(.*?)</title>', html)
            title_text = title.group(1) if title else ""
            # find images
            imgs = re.findall(r'src=["\']([^"\']+)["\']', html)
            upload_imgs = [i for i in imgs if 'wp-content/uploads' in i and 'avatar' not in i and 'logo' not in i]
            # search for price patterns: e.g. 245/KG, 215元/KG, 315/kg, 原價, 特價
            prices = re.findall(r'(\d+)\s*(?:元|/kg|/KG|KG|kg|\s*元/kg|\s*元/KG)', html)
            
            # Find meta description
            desc_m = re.search(r'<meta name="description" content="([^"]+)"', html)
            desc = desc_m.group(1) if desc_m else ""
            
            return {
                "title": title_text,
                "desc": desc,
                "upload_imgs": list(dict.fromkeys(upload_imgs)),
                "prices": list(dict.fromkeys(prices))[:10]
            }
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

skus = ['118583', '110478', '111452', '112390', '87754', '67404', '95123', '89104', '149292']

results = {}
for sku in skus:
    links = get_daybuy_post_for_sku(sku)
    print(f"\nSKU #{sku} -> Links: {links[:2]}")
    if links:
        target_url = links[0]
        data = inspect_daybuy_page(target_url)
        if data:
            results[sku] = {"url": target_url, "data": data}
            print(f"  Title: {data['title']}")
            print(f"  Upload Images: {len(data['upload_imgs'])}")
            for img in data['upload_imgs'][:3]:
                print(f"    - {img}")
            print(f"  Prices found: {data['prices']}")

with open('scripts/daybuy_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
