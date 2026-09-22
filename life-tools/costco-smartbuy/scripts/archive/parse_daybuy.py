import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

filepath = r"C:\Users\BinsonWu\.gemini\antigravity-ide\brain\a632f649-49be-4e5a-8387-ed7c42d4ae08\.system_generated\steps\789\content.md"
with open(filepath, 'r', encoding='utf-8') as f:
    text = f.read()

print("File len:", len(text))

# Look for post content / article body
# Daybuy typically has article body with images and price text
matches = re.findall(r'<div class="[^"]*entry-content[^"]*">(.*?)</div>', text, re.DOTALL)
print("Entry content blocks:", len(matches))
if matches:
    body = matches[0]
    # strip HTML tags
    clean = re.sub(r'<[^>]+>', ' ', body)
    clean = re.sub(r'\s+', ' ', clean)
    print("Clean body text:")
    print(clean[:2000])

# Find all image URLs in the page
imgs = re.findall(r'src=["\']([^"\']+)["\']', text)
upload_imgs = [i for i in imgs if 'wp-content/uploads' in i and 'avatar' not in i and 'logo' not in i]
print(f"\nUpload images ({len(upload_imgs)}):")
for u in list(dict.fromkeys(upload_imgs)):
    print(" ", u)
