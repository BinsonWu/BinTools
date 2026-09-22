#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 01: Build Catalog Tree for Costco Taiwan Food & Dining (c/8)
Accepts:
  --output: Path to save the extracted categories manifest JSON
  --force: Overwrite existing output even if it exists
"""

import os
import sys
import json
import argparse
import urllib.request
import ssl
from datetime import datetime

# Windows encoding safety
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def parse_args():
    parser = argparse.ArgumentParser(description="Step 01: Extract Category 8 hierarchy tree")
    parser.add_argument("--output", required=True, help="Target JSON output path for categories manifest")
    parser.add_argument("--force", action="store_true", help="Force overwrite output if exists")
    return parser.parse_args()

def fetch_category_tree():
    ctx = ssl._create_unverified_context()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'Accept-Language': 'zh-TW,zh;q=0.9',
    }
    url = 'https://www.costco.com.tw/rest/v2/taiwan/catalogs/costcoTaiwanProductCatalog/Online/categories/8'
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
        return json.loads(resp.read().decode('utf-8'))

def flatten_tree(root_node):
    results = []
    seen_ids = set()

    def traverse(node, breadcrumbs=""):
        cid = str(node.get('id', '')).strip()
        name = node.get('name', '').strip()
        url = node.get('url', '').strip()
        subs = node.get('subcategories', [])
        current_path = f"{breadcrumbs} > {name}" if breadcrumbs else name

        is_leaf = len(subs) == 0

        # Avoid redundant duplicate IDs in the same tree branch
        if cid:
            results.append({
                "id": cid,
                "name": name,
                "path": current_path,
                "url": url,
                "is_leaf": is_leaf,
                "sub_count": len(subs)
            })
            seen_ids.add(cid)

        for sub in subs:
            traverse(sub, current_path)

    traverse(root_node)
    return results

def main():
    args = parse_args()
    output_path = os.path.abspath(args.output)

    if os.path.exists(output_path) and not args.force:
        print(f"[SKIP] Output already exists at {output_path}. Use --force to rerun.")
        return 0

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print(f"[*] Fetching Costco Taiwan Food & Dining category tree from official Hybris API...")

    raw_tree = fetch_category_tree()
    flat_categories = flatten_tree(raw_tree)

    manifest = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "root_category_id": "8",
        "root_category_name": raw_tree.get("name", "食品飲料"),
        "total_nodes": len(flat_categories),
        "categories": flat_categories
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"[SUCCESS] Step 01 finished. Discovered {len(flat_categories)} category nodes.")
    print(f"[OUTPUT] Saved manifest to {output_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
