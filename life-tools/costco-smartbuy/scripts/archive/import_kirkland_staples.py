"""
Batch import Kirkland Signature (科克蘭) food, grocery, oil, and nuts staples into Costco Tracker.
"""

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.add_product import add_or_update_product

# 16 iconic Kirkland Signature staples
KS_ITEMS = [
    {"sku": "1236329", "category": "pantry", "discount": 0},   # 科克蘭 Terra Di Bari初榨橄欖油 1公升
    {"sku": "1789247", "category": "pantry", "discount": 0},   # 科克蘭 橄欖油 3公升
    {"sku": "1310208", "category": "pantry", "discount": 0},   # 科克蘭 西班牙冷壓初榨橄欖油 3公升
    {"sku": "1058619", "category": "pantry", "discount": 0},   # 科克蘭 冷萃特級初榨橄欖油 2公升
    {"sku": "999987",  "category": "snacks", "discount": 50},  # 科克蘭 核桃 1.36公斤 (現折 $50)
    {"sku": "1671929", "category": "snacks", "discount": 0},   # 科克蘭 無調味綜合堅果 1.13公斤
    {"sku": "1512209", "category": "snacks", "discount": 0},   # 科克蘭 無調味綜合堅果隨手包 45g X 21包
    {"sku": "583577",  "category": "snacks", "discount": 0},   # 科克蘭 無籽加州李乾 1.58公斤
    {"sku": "968318",  "category": "snacks", "discount": 0},   # 科克蘭 藍莓乾 567公克
    {"sku": "1030484", "category": "pantry", "discount": 0},   # 科克蘭 哥倫比亞咖啡豆 1.36公斤
    {"sku": "1861693", "category": "pantry", "discount": 0},   # 科克蘭 精選中焙咖啡豆 1.13公斤
    {"sku": "1217294", "category": "pantry", "discount": 0},   # 科克蘭 有機衣索匹亞咖啡豆 907公克
    {"sku": "1802065", "category": "pantry", "discount": 0},   # Kirkland Signature 氣泡水 500ml X 35瓶
    {"sku": "7777000", "category": "seafood", "discount": 0},  # 科克蘭 冷凍帶尾特大養殖生蝦仁 908g
    {"sku": "2255551", "category": "seafood", "discount": 0},  # 科克蘭 冷凍養殖帶尾超大生蝦仁 908g
    {"sku": "7777001", "category": "seafood", "discount": 0},  # 科克蘭 冷凍養殖去殼去尾大生蝦仁 907g
]

if __name__ == "__main__":
    print(f"=== Starting Batch Import for {len(KS_ITEMS)} Kirkland Signature Staples ===")
    for item in KS_ITEMS:
        try:
            add_or_update_product(item["sku"], category=item["category"], discount=item["discount"])
        except Exception as e:
            print(f"[ERROR] Failed importing #{item['sku']}: {e}")
    print("=== Finished Batch Import for Kirkland Signature Staples ===")
