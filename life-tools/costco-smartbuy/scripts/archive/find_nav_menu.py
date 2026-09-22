import sys
import urllib.request
import ssl
import re

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl._create_unverified_context()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept-Language': 'zh-TW,zh;q=0.9',
}

url = 'https://www.costco.com.tw/Food-Dining/c/8'
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

# Find navigation links in menu
nav_links = re.findall(r'<a[^>]+href=[\'"]([^\'"]*Food-Dining[^\'"]*)[\'"][^>]*>(.*?)</a>', html, re.DOTALL)
print(f"Total nav links with Food-Dining: {len(nav_links)}")

category_map = {}
for link, text in nav_links:
    clean_text = re.sub(r'<[^>]+>', '', text).strip()
    if '/c/' in link:
        category_map[link] = clean_text

print(f"\nUnique category /c/ links found ({len(category_map)}):")
for link, name in sorted(category_map.items()):
    print(f"  {link} -> {name}")
