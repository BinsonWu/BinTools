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

urls = [
    ('118583', 'https://www.costco.com.tw/Warehouse-Only/Food-Beverages/Seafood-Meat/Chilled-Taiwan-Boneless-Chicken-Leg-Vacuum-Pack/p/118583'),
    ('110478', 'https://www.costco.com.tw/Warehouse-Only/Food-Beverages/Seafood-Meat/Chilled-Taiwan-Boneless-Chicken-Breast-Vacuum-Pack/p/110478'),
    ('149292', 'https://www.costco.com.tw/Warehouse-Only/Food-Beverages/Seafood-Meat/Chilled-Holy-Chicken-Thigh-Vacuum-Pack/p/149292'),
    ('150408', 'https://www.costco.com.tw/Warehouse-Only/Food-Beverages/Seafood-Meat/Taiwan-Native-Boneless-Chicken-Thighs/p/150408'),
    ('159889', 'https://www.costco.com.tw/Warehouse-Only/Food-Beverages/Seafood-Meat/Taiwan-Marinated-Boneless-Chicken-Thighs-With-Basil/p/159889'),
]

for code, u in urls:
    req = urllib.request.Request(u, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            og_img = re.search(r'<meta property="og:image" content="([^"]+)"', html)
            og_title = re.search(r'<meta property="og:title" content="([^"]+)"', html)
            print(f"#{code}: {og_title.group(1) if og_title else ''}")
            print(f"   Official Costco Image: {og_img.group(1) if og_img else 'None'}")
    except Exception as e:
        print(f"#{code} fetch error: {e}")
