import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

filepath = r"C:\Users\BinsonWu\.gemini\antigravity-ide\brain\a632f649-49be-4e5a-8387-ed7c42d4ae08\.system_generated\steps\789\content.md"
with open(filepath, 'r', encoding='utf-8') as f:
    text = f.read()

# Find occurrences of IMG_7778 or price
for img_name in ['IMG_7778', 'IMG_7779', 'IMG_8907', 'IMG_8908', 'LINE_ALBUM']:
    idx = text.find(img_name)
    if idx != -1:
        print(f"\n=== Context for {img_name} ===")
        snippet = text[max(0, idx - 400):min(len(text), idx + 600)]
        clean_snip = re.sub(r'<[^>]+>', ' ', snippet)
        clean_snip = re.sub(r'\s+', ' ', clean_snip)
        print(clean_snip)
