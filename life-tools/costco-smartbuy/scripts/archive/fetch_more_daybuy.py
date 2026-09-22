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

search_targets = [
    ('111452_pork_collar', '台灣豬梅花真空包'),
    ('112390_pork_belly', '台灣豬五花火鍋片'),
    ('150408_chicken_thigh', '台灣土雞去骨清雞腿'),
    ('159889_basil_thigh', '羅勒去骨清雞腿'),
    ('163878_spicy_thigh', '韓式香辣清雞腿'),
    ('13988_rotisserie', '好市多 烤雞'),
]

for tag, kw in search_targets:
    url = f"https://www.daybuy.tw/?s={urllib.parse.quote(kw)}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            posts = re.findall(r'href=[\'"](https://www\.daybuy\.tw/costco/\d+/)[\'"][^>]*>([^<]+)</a>', html)
            print(f"\nKeyword '{kw}' results ({len(posts)}):")
            for p_url, p_title in posts[:3]:
                print(f"  {p_title} -> {p_url}")
                # fetch post and find price or photos
                req2 = urllib.request.Request(p_url, headers=headers)
                with urllib.request.urlopen(req2, context=ctx, timeout=10) as resp2:
                    p_html = resp2.read().decode('utf-8', errors='ignore')
                    imgs = re.findall(r'src=["\'](https://static\.daybuy\.tw/wp-content/uploads/[^"\']+\.(?:jpg|jpeg|png))["\']', p_html)
                    imgs = [i for i in imgs if 'LOGO' not in i and 'avatar' not in i]
                    if imgs:
                        lpath = f"scripts/daybuy_img/{tag}.jpg"
                        cmd = f'curl.exe -s -L -k "{imgs[0]}" -o "{lpath}"'
                        subprocess.run(cmd, shell=True)
                        print(f"    Saved photo to {lpath} ({imgs[0]})")
    except Exception as e:
        print(f"Error {kw}: {e}")
