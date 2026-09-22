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

keywords = [
    ('益活雞冷藏去骨清雞腿', 'https://www.daybuy.tw/costco/163365/'),
    ('台灣去骨清雞腿真空包', 'https://www.daybuy.tw/costco/81651/'),
    ('台灣雞清胸肉真空包', 'https://www.daybuy.tw/costco/81120/'),
    ('台灣冷藏豬五花', 'https://www.daybuy.tw/?s=' + urllib.parse.quote('豬五花肉片')),
    ('台灣冷藏豬梅花', 'https://www.daybuy.tw/?s=' + urllib.parse.quote('冷藏豬梅花')),
    ('無骨牛小排', 'https://www.daybuy.tw/?s=' + urllib.parse.quote('無骨牛小排 燒烤片')),
    ('嫩肩里肌', 'https://www.daybuy.tw/?s=' + urllib.parse.quote('嫩肩里肌真空包')),
    ('牛肋條', 'https://www.daybuy.tw/?s=' + urllib.parse.quote('牛肋條真空包')),
]

for name, url in keywords:
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            if 'costco/' in url:
                # Detail page
                title = re.search(r'<title>(.*?)</title>', html)
                imgs = re.findall(r'src=["\']([^"\']+)["\']', html)
                up_imgs = [i for i in imgs if 'wp-content/uploads' in i and 'avatar' not in i and 'logo' not in i]
                print(f"=== {name} ({url}) ===")
                print(f"  Title: {title.group(1) if title else ''}")
                print(f"  Images: {len(up_imgs)}")
                for img in up_imgs[:3]:
                    print(f"    {img}")
            else:
                # Search page
                posts = re.findall(r'href=[\'"](https://www\.daybuy\.tw/costco/\d+/)[\'"][^>]*>([^<]+)</a>', html)
                print(f"Search '{name}':")
                for p_url, p_title in posts[:4]:
                    print(f"  {p_title} -> {p_url}")
    except Exception as e:
        print(f"Error {name}: {e}")
