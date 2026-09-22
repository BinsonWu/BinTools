import urllib.request
import ssl
import re

ctx = ssl._create_unverified_context()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
}
url = 'https://www.costco.com.tw/c/hot-buys'
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print('Hot Buys HTML len:', len(html))
        # Find product links
        links = re.findall(r'href=[\'"]([^\'"]+/p/\d+)[\'"]', html)
        unique_links = list(dict.fromkeys(links))
        print('Found unique /p/ links:', len(unique_links))
        for l in unique_links[:15]:
            print('  Link:', l)
except Exception as e:
    print('Error:', e)
