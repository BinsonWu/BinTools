import sys
import urllib.request
import ssl
import json

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl._create_unverified_context()
headers = {'User-Agent': 'Mozilla/5.0'}

url = "https://www.costco.com.tw/rest/v2/taiwan/products/search?query=" + urllib.parse.quote(":relevance:allCategories:8") + "&pageSize=1"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    facets = data.get('facets', [])
    for f in facets:
        print(f"Facet: {f.get('name')} (code: {f.get('code')})")
        for val in f.get('values', []):
            print(f"  - {val.get('name')} ({val.get('count')}) query: {val.get('query', {}).get('query', {}).get('value')}")
