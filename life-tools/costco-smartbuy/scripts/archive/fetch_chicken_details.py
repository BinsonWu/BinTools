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

posts = [
    ('150408_native_chicken', 'https://www.daybuy.tw/costco/174352/'),
    ('159889_basil_chicken', 'https://www.daybuy.tw/costco/235635/'),
    ('163878_korean_chicken', 'https://www.daybuy.tw/costco/268896/'),
]

for name, url in posts:
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            title = re.search(r'<title>(.*?)</title>', html)
            print(f"\n=== {title.group(1) if title else name} ===")
            imgs = re.findall(r'src=["\'](https://static\.daybuy\.tw/wp-content/uploads/[^"\']+\.(?:jpg|jpeg|png))["\']', html)
            imgs = [i for i in imgs if 'LOGO' not in i and 'avatar' not in i]
            for i, img_url in enumerate(imgs[:3]):
                lpath = f"scripts/daybuy_img/{name}_{i}.jpg"
                cmd = f'curl.exe -s -L -k "{img_url}" -o "{lpath}"'
                subprocess.run(cmd, shell=True)
                print(f"  [{i}] Saved {lpath} -> {img_url}")
    except Exception as e:
        print(f"Error {name}: {e}")
