import urllib.request
import ssl
import re
import sys
import subprocess
import os

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl._create_unverified_context()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept-Language': 'zh-TW,zh;q=0.9',
}

pages = [
    ('118583', 'https://www.daybuy.tw/costco/81651/'),
    ('110478', 'https://www.daybuy.tw/costco/81120/'),
    ('149292', 'https://www.daybuy.tw/costco/163365/'),
    ('35675_beef', 'https://www.daybuy.tw/costco/35675/'),
]

os.makedirs('scripts/daybuy_img', exist_ok=True)

for sku, url in pages:
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            imgs = re.findall(r'src=["\'](https://static\.daybuy\.tw/wp-content/uploads/[^"\']+\.(?:jpg|jpeg|png))["\']', html)
            imgs = [i for i in imgs if 'LOGO' not in i and 'avatar' not in i]
            print(f"\nPage {sku} ({url}) has {len(imgs)} photos:")
            for i, img_url in enumerate(imgs[:4]):
                print(f"  [{i}] {img_url}")
                # Download first 2 photos for each
                local_path = f"scripts/daybuy_img/{sku}_{i}.jpg"
                cmd = f'curl.exe -s -L -k "{img_url}" -o "{local_path}"'
                subprocess.run(cmd, shell=True)
                if os.path.exists(local_path):
                    print(f"      Saved {local_path} ({os.path.getsize(local_path)} bytes)")
    except Exception as e:
        print(f"Error {sku}: {e}")
