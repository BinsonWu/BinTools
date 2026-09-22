import subprocess
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB_IMG = os.path.join(PROJECT_ROOT, "public", "images", "products")
DIST_IMG = os.path.join(PROJECT_ROOT, "dist", "images", "products")
os.makedirs(PUB_IMG, exist_ok=True)
os.makedirs(DIST_IMG, exist_ok=True)

targets = [
    ("costco-133600.jpg", "https://www.costco.com.tw/medias/sys_master/images/h84/h47/82280482930718.jpg"),
    ("costco-133321.jpg", "https://www.costco.com.tw/medias/sys_master/images/h21/h05/70333773971486.jpg"),
    ("costco-146146.jpg", "https://www.costco.com.tw/medias/sys_master/images/h6d/h3d/70333786095646.jpg"),
    ("costco-159017.jpg", "https://www.costco.com.tw/medias/sys_master/images/hdc/h70/418236627451934.jpg"),
    ("costco-157706.jpg", "https://www.costco.com.tw/medias/sys_master/images/h54/hf7/402145330528286.jpg"),
]

for filename, url in targets:
    p_dest = os.path.join(PUB_IMG, filename)
    d_dest = os.path.join(DIST_IMG, filename)
    print(f"Downloading {filename}...")
    cmd = f'curl.exe -s -L -k "{url}" -o "{p_dest}"'
    res = subprocess.run(cmd, shell=True)
    if res.returncode == 0 and os.path.exists(p_dest) and os.path.getsize(p_dest) > 1000:
        import shutil
        shutil.copy2(p_dest, d_dest)
        print(f"  [OK] Saved {filename} ({os.path.getsize(p_dest)} bytes)")
    else:
        print(f"  [FAIL] Could not download {filename}")
