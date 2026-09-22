import urllib.request
import ssl
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl._create_unverified_context()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
}

url = 'https://www.costco.com.tw/c/hot-buys'
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

# Extract product card blocks
# Typical hybris / angular product card has class 'product-item' or 'lister-item' or similar
cards = re.findall(r'<div[^>]*class="[^"]*product-item[^"]*"[^>]*>.*?</div>\s*</div>\s*</div>', html, re.DOTALL)
if not cards:
    cards = re.findall(r'<div[^>]*class="[^"]*lister__item[^"]*"[^>]*>.*?</div>\s*</div>', html, re.DOTALL)

print('Cards found:', len(cards))
if cards:
    print('Card 0 snippet:\n', cards[0][:800])
else:
    # let's search for 463663 container
    idx = html.find('463663')
    print('463663 context:\n', html[idx-200:idx+600])
