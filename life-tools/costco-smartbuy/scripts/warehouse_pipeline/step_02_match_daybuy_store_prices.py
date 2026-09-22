#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 02: Match Warehouse-Only & Uber Eats products with Daybuy.tw in-store prices
Concurrent multithreaded version with seed caching and robust checkpointing.
Accepts:
  --input: Path to raw warehouse products JSON (from step 01)
  --output: Target JSON file path
  --workers: Number of concurrent threads (default: 6)
  --force: Overwrite existing output
"""

import os
import sys
import json
import time
import re
import argparse
import urllib.request
import ssl
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from bs4 import BeautifulSoup

# Windows encoding safety
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def parse_args():
    parser = argparse.ArgumentParser(description="Step 02: Match Daybuy in-store prices")
    parser.add_argument("--input", required=True, help="Path to raw warehouse products JSON")
    parser.add_argument("--output", required=True, help="Path to save matched Daybuy prices JSON")
    parser.add_argument("--workers", type=int, default=6, help="Concurrent workers")
    parser.add_argument("--force", action="store_true", help="Force overwrite output if exists")
    return parser.parse_args()

def search_daybuy_sku(sku, ctx, headers):
    search_url = f"https://www.daybuy.tw/?s={sku}"
    req = urllib.request.Request(search_url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=12) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            
            post_url = None
            for a in soup.find_all('a', href=re.compile(r'/costco/\d+/')):
                txt = a.get_text() + " " + a.get('title', '')
                if sku in txt:
                    post_url = a['href']
                    break
            if not post_url:
                first = soup.find('a', href=re.compile(r'/costco/\d+/'))
                if first:
                    post_url = first['href']
            return post_url
    except Exception:
        return None

def extract_daybuy_post_info(post_url, sku, ctx, headers):
    req = urllib.request.Request(post_url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            
            price_raw = None
            price_per_kg = None
            is_by_weight = False
            fixed_price = None
            weight_text = None
            
            # 1. Parse tables
            for tr in soup.select('table tr'):
                row_text = tr.get_text(' | ', strip=True)
                if '原價' in row_text or '價格' in row_text:
                    m_kg = re.search(r'(\d+(?:\.\d+)?)\s*/\s*KG', row_text, re.IGNORECASE)
                    if m_kg:
                        price_per_kg = float(m_kg.group(1))
                        is_by_weight = True
                        price_raw = m_kg.group(0)
                    else:
                        m_price = re.search(r'(\d+(?:,\d+)?)\s*元', row_text)
                        if m_price:
                            fixed_price = float(m_price.group(1).replace(',', ''))
                            price_raw = m_price.group(0)
                            
                if '重量' in row_text or '數量' in row_text:
                    weight_text = row_text
                    
            # 2. Body cell text fallback
            if price_per_kg is None and fixed_price is None:
                m_kg = re.search(r'(\d+(?:\.\d+)?)\s*/\s*KG', html, re.IGNORECASE)
                if m_kg:
                    price_per_kg = float(m_kg.group(1))
                    is_by_weight = True
                    price_raw = m_kg.group(0)
                else:
                    m_price = re.search(r'class="bdt-static-body-row-cell-text">\s*([0-9,]+)\s*元', html)
                    if m_price:
                        fixed_price = float(m_price.group(1).replace(',', ''))
                        price_raw = m_price.group(1) + " 元"
                        
            # Photos
            img_url = None
            for img in soup.find_all('img'):
                src = img.get('src') or img.get('data-src') or ''
                if '/uploads/' in src and ('daybuy' in src or 'static' in src):
                    if not any(x in src.lower() for x in ['logo', 'icon', 'avatar', 'banner']):
                        img_url = src
                        break
                        
            post_id_match = re.search(r'/costco/(\d+)/', post_url)
            post_id = post_id_match.group(1) if post_id_match else None

            return {
                "daybuy_url": post_url,
                "post_id": post_id,
                "price_raw": price_raw,
                "price_per_kg": price_per_kg,
                "fixed_price": fixed_price,
                "is_by_weight": is_by_weight,
                "weight_text": weight_text,
                "daybuy_image_url": img_url
            }
    except Exception:
        return None

def download_image(img_url, sku, output_dir, ctx, headers):
    try:
        ext = '.jpg'
        if '.png' in img_url.lower():
            ext = '.png'
        filename = f"daybuy_{sku}{ext}"
        target_path = os.path.join(output_dir, filename)
        if os.path.exists(target_path) and os.path.getsize(target_path) > 1000:
            return f"/images/products/{filename}"
            
        req = urllib.request.Request(img_url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=12) as resp:
            data = resp.read()
            if len(data) > 1000:
                with open(target_path, 'wb') as f:
                    f.write(data)
                return f"/images/products/{filename}"
    except Exception:
        pass
    return None

def process_single_product(p, ctx, headers, img_dir):
    sku = str(p.get('code', '')).strip()
    name = p.get('name', '')
    if not sku:
        return None, None

    post_url = search_daybuy_sku(sku, ctx, headers)
    time.sleep(0.15)
    
    info = None
    if post_url:
        info = extract_daybuy_post_info(post_url, sku, ctx, headers)
        time.sleep(0.15)
        
    if info and (info.get('price_per_kg') or info.get('fixed_price')):
        local_img = None
        if info.get('daybuy_image_url'):
            local_img = download_image(info['daybuy_image_url'], sku, img_dir, ctx, headers)
            info['local_image_path'] = local_img
            
        res = {
            "sku": sku,
            "name": name,
            "found": True,
            **info
        }
        return sku, res
    else:
        res = {
            "sku": sku,
            "name": name,
            "found": False,
            "daybuy_url": post_url
        }
        return sku, res

def main():
    args = parse_args()
    input_path = os.path.abspath(args.input)
    output_path = os.path.abspath(args.output)
    workers = max(1, min(args.workers, 8))
    
    if not os.path.exists(input_path):
        print(f"[ERROR] Input manifest not found: {input_path}", flush=True)
        return 1
        
    if os.path.exists(output_path) and not args.force:
        print(f"[SKIP] Output already exists at {output_path}. Use --force to rerun.", flush=True)
        return 0
        
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        products = data.get('products', [])
        
    print(f"[*] Step 02: Loaded {len(products)} products. Matching Daybuy prices with {workers} workers...", flush=True)
    
    ctx = ssl._create_unverified_context()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    }
    
    img_dir = os.path.abspath("public/images/products")
    os.makedirs(img_dir, exist_ok=True)
    
    matched_results = {}
    lock = threading.Lock()
    
    # 1. Seed cache from previous daybuy_price_verification workspace
    seed_cache_file = os.path.abspath(".agent_workspace/daybuy_price_verification/daybuy_scraped_results.json")
    if os.path.exists(seed_cache_file):
        try:
            with open(seed_cache_file, 'r', encoding='utf-8') as f:
                seed = json.load(f).get('results', {})
                for k, v in seed.items():
                    if v.get('found') and (v.get('price_per_kg') or v.get('fixed_price')):
                        matched_results[k] = v
            print(f"[+] Loaded {len(matched_results)} cached items from Daybuy verification workspace.", flush=True)
        except Exception:
            pass

    # 2. Check if partial cached file exists in current workspace
    if os.path.exists(output_path) and not args.force:
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                old = json.load(f)
                for k, v in old.get('matched_products', {}).items():
                    matched_results[k] = v
            print(f"[+] Loaded {len(matched_results)} existing matched items from {output_path}.", flush=True)
        except Exception:
            pass

    pending_products = [p for p in products if str(p.get('code', '')).strip() not in matched_results]
    print(f"[*] Pending items to query: {len(pending_products)} (Already cached: {len(matched_results)})", flush=True)

    completed_count = len(matched_results)
    matched_count = sum(1 for v in matched_results.values() if v.get('found') and (v.get('price_per_kg') or v.get('fixed_price')))
    total = len(products)
    save_counter = 0

    def save_checkpoint():
        manifest = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_scanned": len(matched_results),
            "matched_count": sum(1 for v in matched_results.values() if v.get('found') and (v.get('price_per_kg') or v.get('fixed_price'))),
            "matched_products": matched_results
        }
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_sku = {
            executor.submit(process_single_product, p, ctx, headers, img_dir): str(p.get('code', '')).strip()
            for p in pending_products
        }
        
        for future in as_completed(future_to_sku):
            sku = future_to_sku[future]
            try:
                sku_res, res = future.result()
                if sku_res and res:
                    with lock:
                        matched_results[sku_res] = res
                        completed_count += 1
                        save_counter += 1
                        if res.get('found'):
                            matched_count += 1
                            price_display = f"{res.get('price_per_kg')}/KG" if res.get('is_by_weight') else f"NT$ {res.get('fixed_price')}"
                            print(f"[{completed_count}/{total}] #{sku_res}: {res.get('name', '')[:20]} -> Matched: {price_display}", flush=True)
                        else:
                            if completed_count % 20 == 0:
                                print(f"[{completed_count}/{total}] Progress: {matched_count} prices matched...", flush=True)
                                
                        if save_counter >= 25:
                            save_checkpoint()
                            save_counter = 0
            except Exception as e:
                pass

    save_checkpoint()
    final_matched = sum(1 for v in matched_results.values() if v.get('found') and (v.get('price_per_kg') or v.get('fixed_price')))
    print(f"\n[SUCCESS] Step 02 finished. Successfully matched {final_matched}/{total} store prices from Daybuy.", flush=True)
    print(f"[OUTPUT] Saved to {output_path}", flush=True)
    return 0

if __name__ == '__main__':
    sys.exit(main())
