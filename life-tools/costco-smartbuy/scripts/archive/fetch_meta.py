import urllib.request
import ssl
import re
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl._create_unverified_context()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
}

ITEMS_TO_FETCH = [
    {"sku": "463663", "url": "https://www.costco.com.tw/Food-Dining/Frozen-Fresh-Food/Frozen-Seafood-Meat/Frozen-Lightly-Salted-Mackerel-800-g/p/463663"},
    {"sku": "8500806", "url": "https://www.costco.com.tw/Food-Dining/Frozen-Fresh-Food/Frozen-Meals/Dachan-Frozen-Yakitori-480-g/p/8500806"},
    {"sku": "398703", "url": "https://www.costco.com.tw/Food-Dining/Drinks/Coffee/UCC-Drip-Coffee-7-g-X-75-Count/p/398703"},
    {"sku": "101329", "url": "https://www.costco.com.tw/Food-Dining/Drinks/Coffee/Onefreshcup-Gayo-Mandheling-Drip-Coffee-11-g-X-50-Count/p/101329"},
    {"sku": "97313", "url": "https://www.costco.com.tw/c/AGV-100-Oatmeal-Drink-340-ml-X-12-Count/p/97313"},
    {"sku": "145957", "url": "https://www.costco.com.tw/Food-Dining/Drinks/Beverages-Juice/IF-Pure-Coconut-Water-1-L-X-6-Count/p/145957"},
    {"sku": "63005", "url": "https://www.costco.com.tw/Food-Dining/Snacks/Candies-Chocolates/Snickers-Minis-Chocolate-9-g-X-126-Count/p/63005"},
    {"sku": "307304", "url": "https://www.costco.com.tw/Food-Dining/Groceries/Baking-Dried-Goods/BeeTouched-Beelove-Taiwan-Mountains-Honey-Gift-Pack-700-g-X-2-Pack/p/307304"},
    {"sku": "106150", "url": "https://www.costco.com.tw/Cha-Wu-Le/Cha-Wu-Le-Burdock-Tea-5-g-X-60-Count/p/106150"},
    {"sku": "145184", "url": "https://www.costco.com.tw/c/Brands-Essence-of-Chicken-68-ml-X-30-Count-41-ml-X-2-Count/p/145184"},
    {"sku": "326800", "url": "https://www.costco.com.tw/p/326800"},
    {"sku": "435364", "url": "https://www.costco.com.tw/p/435364"},
    {"sku": "119169", "url": "https://www.costco.com.tw/p/119169"}
]

results = {}
for item in ITEMS_TO_FETCH:
    sku = item["sku"]
    url = item["url"]
    print(f"Fetching SKU #{sku}...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=12) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            
            # Extract og:image
            og_img = re.search(r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)["\']', html)
            if not og_img:
                og_img = re.search(r'content=["\']([^"\']+)["\']\s+property=["\']og:image["\']', html)
            
            # Extract og:title
            og_title = re.search(r'<meta\s+property=["\']og:title["\']\s+content=["\']([^"\']+)["\']', html)
            if not og_title:
                og_title = re.search(r'<title>([^<]+)</title>', html)
                
            # Extract price from jsonld
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

with open(r'scripts/fetched_promo_items.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("Finished saving fetched_promo_items.json")
