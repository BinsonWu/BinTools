import urllib.request
import ssl
from bs4 import BeautifulSoup
import re
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')
ctx = ssl._create_unverified_context()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

url = 'https://www.costco.com.tw/Warehouse-Only/Food-Beverages/c/WH08?pageSize=100'
req = urllib.request.Request(url, headers=headers)
try:
    html = urllib.request.urlopen(req, context=ctx, timeout=20).read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    links = soup.find_all('a', href=re.compile(r'/p/(\d+)'))
    print(f'Total /p/ links: {len(links)}')

    seen = {}
    for a in links:
        m = re.search(r'/p/(\d+)', a.get('href', ''))
        if m:
            code = m.group(1)
            name = a.text.strip() or a.get('title', '').strip()
            img = a.find('img')
            img_src = img.get('src') if img else None
            if code not in seen or (not seen[code]['name'] and name):
                if code not in seen:
                    seen[code] = {'code': code, 'name': name, 'href': a.get('href'), 'img': img_src}
                else:
                    if name:
                        seen[code]['name'] = name
                    if img_src and not seen[code]['img']:
                        seen[code]['img'] = img_src

    print(f'Unique products on page: {len(seen)}')
    for code, info in list(seen.items())[:15]:
        print(f"#{code}: {info['name']} | img={info['img']}")

except Exception as e:
    print(f"Error: {e}")
