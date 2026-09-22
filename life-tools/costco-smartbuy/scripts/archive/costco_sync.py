import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import sqlite3
import json
import urllib.request
import ssl
import time

PROJECT_ROOT = r"C:\Binson\Mytools\Python\SideProject\Costco"
DB_PATH = os.path.join(PROJECT_ROOT, "costco_products.db")
IMAGES_DIR = os.path.join(PROJECT_ROOT, "public", "images", "products")
OUTPUT_TS = os.path.join(PROJECT_ROOT, "src", "data", "mockProducts.ts")
OUTPUT_JSON = os.path.join(PROJECT_ROOT, "public", "data", "products.json")
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "scripts")

os.makedirs(SCRIPTS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# SSL context for downloading images
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

INITIAL_PRODUCTS = [
    # 1. 牛肉類 (Beef)
    {
        "id": "beef-01",
        "name": "美國特選嫩肩里肌真空包 (Choice)",
        "category": "beef",
        "subCategory": "真空包生鮮原肉",
        "pricingType": "by_weight",
        "pricePerKg": 489,
        "originalPrice": 1369,
        "discountAmount": 150,
        "discountEndDate": "2026-09-27",
        "packageSpec": "整塊真空包 (約 2.8kg 計價)",
        "totalWeightInGrams": 2800,
        "unitType": "g",
        "tagType": "weekly_sale",
        "historicalBenchmark": "historical_low",
        "storageType": "cold",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "67404",
        "verifiedSource": "好市多門市實拍照",
        "historicalRange": {"minPer100g": 44.9, "maxPer100g": 53.9},
        "note": "牌價約 $489/kg，自行修筋分切比分切盒裝便宜超多",
        "imageUrl": "https://images.unsplash.com/photo-1558030006-450675393462?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "beef-02",
        "name": "美國特選牛肋條真空包 (Choice)",
        "category": "beef",
        "subCategory": "真空包生鮮原肉",
        "pricingType": "by_weight",
        "pricePerKg": 659,
        "originalPrice": 1648,
        "discountAmount": 0,
        "discountEndDate": None,
        "packageSpec": "真空包 2入裝 (約 2.5kg)",
        "totalWeightInGrams": 2500,
        "unitType": "g",
        "tagType": "everyday_value",
        "historicalBenchmark": "standard",
        "storageType": "cold",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "95123",
        "verifiedSource": "好市多門市實拍牌價",
        "historicalRange": {"minPer100g": 59.9, "maxPer100g": 69.9},
        "note": "燉牛肉、紅燒、咖哩油香十足",
        "imageUrl": "https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "beef-03",
        "name": "美國特選牛絞肉 (88%瘦肉 12%油)",
        "category": "beef",
        "subCategory": "冷藏盒裝",
        "pricingType": "by_weight",
        "pricePerKg": 340,
        "originalPrice": 748,
        "discountAmount": 0,
        "discountEndDate": None,
        "packageSpec": "大盒分裝 (約 2.2kg)",
        "totalWeightInGrams": 2200,
        "unitType": "g",
        "tagType": "everyday_value",
        "historicalBenchmark": "standard",
        "storageType": "cold",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "11382",
        "verifiedSource": "好市多肉品部標籤",
        "historicalRange": {"minPer100g": 31.9, "maxPer100g": 36.9},
        "note": "自製漢堡排、肉醬麵經典神物",
        "imageUrl": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "beef-04",
        "name": "美國頂級無骨牛小排燒烤片 (Prime)",
        "category": "beef",
        "subCategory": "冷藏盒裝",
        "pricingType": "by_weight",
        "pricePerKg": 1299,
        "originalPrice": 2338,
        "discountAmount": 200,
        "discountEndDate": "2026-09-28",
        "packageSpec": "厚切燒烤盒裝 (約 1.8kg)",
        "totalWeightInGrams": 1800,
        "unitType": "g",
        "tagType": "black_card",
        "historicalBenchmark": "historical_low",
        "storageType": "cold",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "87754",
        "verifiedSource": "今購百科最新牌價",
        "historicalRange": {"minPer100g": 119.0, "maxPer100g": 145.0},
        "note": "黑鑽卡專屬折讓，油花分佈細膩奢華",
        "imageUrl": "https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "beef-05",
        "name": "冷凍美國特選肥牛肉卷 (火鍋/多用途)",
        "category": "beef",
        "subCategory": "冷凍肉品",
        "pricingType": "fixed_package",
        "originalPrice": 989,
        "discountAmount": 90,
        "discountEndDate": "2026-09-29",
        "packageSpec": "大盒薄切卷 (2.0kg)",
        "totalWeightInGrams": 2000,
        "unitType": "g",
        "tagType": "weekly_sale",
        "historicalBenchmark": "historical_low",
        "storageType": "freeze",
        "priceSource": "online_catalog",
        "costcoItemNumber": "147120",
        "verifiedSource": "好市多線上購物",
        "historicalRange": {"minPer100g": 44.9, "maxPer100g": 49.5},
        "note": "好市多線上即時商品 (#147120)，牛丼燒肉片必備",
        "imageUrl": "https://images.unsplash.com/photo-1551024709-8f23befc6f87?w=600&auto=format&fit=crop&q=80"
    },

    # 2. 雞肉類 (Chicken)
    {
        "id": "chicken-01",
        "name": "台灣雞清胸肉真空包 (生鮮冷藏)",
        "category": "chicken",
        "subCategory": "冷藏生鮮",
        "pricingType": "by_weight",
        "pricePerKg": 215,
        "originalPrice": 580,
        "discountAmount": 0,
        "discountEndDate": None,
        "packageSpec": "2.7kg (約6獨立小包，牌價 $215/kg)",
        "totalWeightInGrams": 2700,
        "unitType": "g",
        "tagType": "weekly_sale",
        "historicalBenchmark": "standard",
        "storageType": "cold",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "110478",
        "verifiedSource": "今購百科 2026/09 實拍照",
        "historicalRange": {"minPer100g": 17.9, "maxPer100g": 22.9},
        "note": "好市多門市實拍牌價 NT$ 215/kg (#110478)。單包約 2.7kg 總價約 $580，換算每 100g 為 NT$ 21.5！健身必囤神物",
        "imageUrl": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "chicken-02",
        "name": "冷藏台灣去骨清雞腿真空包",
        "category": "chicken",
        "subCategory": "冷藏生鮮",
        "pricingType": "by_weight",
        "pricePerKg": 222,
        "originalPrice": 599,
        "discountAmount": 0,
        "discountEndDate": None,
        "packageSpec": "2.7kg (約6獨立真空包)",
        "totalWeightInGrams": 2700,
        "unitType": "g",
        "tagType": "everyday_value",
        "historicalBenchmark": "standard",
        "storageType": "cold",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "118583",
        "verifiedSource": "好市多冷藏肉品標牌",
        "historicalRange": {"minPer100g": 20.9, "maxPer100g": 24.5},
        "note": "賣場限定生鮮秤重，常態牌價約 $222/kg。去大骨留腿排，香煎肉嫩皮脆",
        "imageUrl": "https://images.unsplash.com/photo-1587593810167-a84920ea0781?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "chicken-03",
        "name": "台灣冷藏雞清里肌肉 (小里肌)",
        "category": "chicken",
        "subCategory": "冷藏生鮮",
        "pricingType": "by_weight",
        "pricePerKg": 200,
        "originalPrice": 499,
        "discountAmount": 40,
        "discountEndDate": "2026-09-25",
        "packageSpec": "2.5kg (多小包入)",
        "totalWeightInGrams": 2500,
        "unitType": "g",
        "tagType": "weekly_sale",
        "historicalBenchmark": "historical_low",
        "storageType": "cold",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "119420",
        "verifiedSource": "好市多門市標籤",
        "historicalRange": {"minPer100g": 18.0, "maxPer100g": 22.0},
        "note": "牌價約 $200/kg，肉質極嫩無筋膜，減脂首選",
        "imageUrl": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "chicken-04",
        "name": "好市多熟食部美式烤全雞 (現烤熱騰騰)",
        "category": "chicken",
        "subCategory": "熟食部",
        "pricingType": "fixed_package",
        "originalPrice": 189,
        "discountAmount": 0,
        "discountEndDate": None,
        "packageSpec": "全雞 1入 (約 1.3kg)",
        "totalWeightInGrams": 1300,
        "unitType": "g",
        "tagType": "everyday_value",
        "historicalBenchmark": "historical_low",
        "storageType": "room",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "13988",
        "verifiedSource": "熟食部現烤標價牌",
        "historicalRange": {"minPer100g": 13.5, "maxPer100g": 14.5},
        "note": "熟食即食，CP值破表的常駐肉品王者",
        "imageUrl": "https://images.unsplash.com/photo-1598103442097-8b74394b95c6?w=600&auto=format&fit=crop&q=80"
    },

    # 3. 豬肉類 (Pork)
    {
        "id": "pork-01",
        "name": "台灣冷藏豬梅花真空包 (原肉塊)",
        "category": "pork",
        "subCategory": "冷藏生鮮",
        "pricingType": "by_weight",
        "pricePerKg": 270,
        "originalPrice": 648,
        "discountAmount": 70,
        "discountEndDate": "2026-09-26",
        "packageSpec": "單包真空 (約 2.4kg)",
        "totalWeightInGrams": 2400,
        "unitType": "g",
        "tagType": "weekly_sale",
        "historicalBenchmark": "historical_low",
        "storageType": "cold",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "111452",
        "verifiedSource": "好市多生鮮標牌",
        "historicalRange": {"minPer100g": 24.0, "maxPer100g": 29.0},
        "note": "肥瘦適中，可切叉燒肉或厚切豬排",
        "imageUrl": "https://images.unsplash.com/photo-1432139555190-58524dae6a55?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "pork-02",
        "name": "台灣冷藏豬五花火鍋薄肉片",
        "category": "pork",
        "subCategory": "冷藏盒裝",
        "pricingType": "by_weight",
        "pricePerKg": 315,
        "originalPrice": 629,
        "discountAmount": 0,
        "discountEndDate": None,
        "packageSpec": "盒裝三層 (約 2.0kg)",
        "totalWeightInGrams": 2000,
        "unitType": "g",
        "tagType": "everyday_value",
        "historicalBenchmark": "standard",
        "storageType": "cold",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "112390",
        "verifiedSource": "好市多生鮮標牌",
        "historicalRange": {"minPer100g": 28.5, "maxPer100g": 33.5},
        "note": "涮火鍋、蒜泥白肉常備",
        "imageUrl": "https://images.unsplash.com/photo-1602498456745-e9503b30470b?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "pork-03",
        "name": "台灣冷藏豬大排骨 (切塊)",
        "category": "pork",
        "subCategory": "冷藏盒裝",
        "pricingType": "by_weight",
        "pricePerKg": 170,
        "originalPrice": 425,
        "discountAmount": 0,
        "discountEndDate": None,
        "packageSpec": "煲湯切塊 (約 2.5kg)",
        "totalWeightInGrams": 2500,
        "unitType": "g",
        "tagType": "everyday_value",
        "historicalBenchmark": "historical_low",
        "storageType": "cold",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "115401",
        "verifiedSource": "好市多冷藏標牌",
        "historicalRange": {"minPer100g": 15.0, "maxPer100g": 19.0},
        "note": "熬湯底、蘿蔔排骨湯極致鮮甜",
        "imageUrl": "https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "pork-04",
        "name": "台灣冷藏豬里肌厚切豬排 (生鮮盒裝)",
        "category": "pork",
        "subCategory": "冷藏生鮮",
        "pricingType": "by_weight",
        "pricePerKg": 260,
        "originalPrice": 520,
        "discountAmount": 40,
        "discountEndDate": "2026-09-28",
        "packageSpec": "厚切 8-10片 (約 2.0kg)",
        "totalWeightInGrams": 2000,
        "unitType": "g",
        "tagType": "weekly_sale",
        "historicalBenchmark": "historical_low",
        "storageType": "cold",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "114882",
        "verifiedSource": "好市多生鮮標牌",
        "historicalRange": {"minPer100g": 23.5, "maxPer100g": 27.5},
        "note": "大片厚切炸豬排、香煎排骨必買",
        "imageUrl": "https://images.unsplash.com/photo-1432139555190-58524dae6a55?w=600&auto=format&fit=crop&q=80"
    },

    # 4. 海鮮水產 (Seafood)
    {
        "id": "seafood-01",
        "name": "空運挪威冷藏鮭魚切片 (生鮮)",
        "category": "seafood",
        "subCategory": "冷藏生鮮",
        "pricingType": "by_weight",
        "pricePerKg": 699,
        "originalPrice": 989,
        "discountAmount": 110,
        "discountEndDate": "2026-09-27",
        "packageSpec": "冷藏 4-5大片 (約 1.4kg)",
        "totalWeightInGrams": 1400,
        "unitType": "g",
        "tagType": "weekly_sale",
        "historicalBenchmark": "historical_low",
        "storageType": "cold",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "89104",
        "verifiedSource": "海鮮部今日牌價",
        "historicalRange": {"minPer100g": 59.9, "maxPer100g": 78.9},
        "note": "油脂滿溢，煎烤生魚片等級鮮度",
        "imageUrl": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "seafood-02",
        "name": "熟凍加拿大松葉蟹鉗腳",
        "category": "seafood",
        "subCategory": "熟凍生鮮",
        "pricingType": "fixed_package",
        "originalPrice": 1499,
        "discountAmount": 200,
        "discountEndDate": "2026-09-30",
        "packageSpec": "盒裝 (約 900g)",
        "totalWeightInGrams": 900,
        "unitType": "g",
        "tagType": "black_card",
        "historicalBenchmark": "historical_low",
        "storageType": "freeze",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "124981",
        "verifiedSource": "今購百科社群情報",
        "historicalRange": {"minPer100g": 144.0, "maxPer100g": 166.5},
        "note": "黑鑽會員獨享折價，解凍即食肉質鮮甜",
        "imageUrl": "https://images.unsplash.com/photo-1559742811-822873691df8?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "seafood-03",
        "name": "冷凍超大黑虎蝦 16/20 (帶頭帶殼)",
        "category": "seafood",
        "subCategory": "冷凍水產",
        "pricingType": "fixed_package",
        "originalPrice": 799,
        "discountAmount": 0,
        "discountEndDate": None,
        "packageSpec": "盒裝約 16-20尾 (1.0kg)",
        "totalWeightInGrams": 1000,
        "unitType": "g",
        "tagType": "everyday_value",
        "historicalBenchmark": "standard",
        "storageType": "freeze",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "109482",
        "verifiedSource": "好市多冷凍水產標牌",
        "historicalRange": {"minPer100g": 74.9, "maxPer100g": 84.9},
        "note": "緊實彈牙，鹽焗或燒烤聚餐熱門",
        "imageUrl": "https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "seafood-04",
        "name": "冷凍台灣金目鱸魚排 (單片真空)",
        "category": "seafood",
        "subCategory": "冷凍水產",
        "pricingType": "fixed_package",
        "originalPrice": 479,
        "discountAmount": 50,
        "discountEndDate": "2026-09-24",
        "packageSpec": "1.2kg (約 5-6片真空包)",
        "totalWeightInGrams": 1200,
        "unitType": "g",
        "tagType": "weekly_sale",
        "historicalBenchmark": "historical_low",
        "storageType": "freeze",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "133982",
        "verifiedSource": "好市多現場特價牆",
        "historicalRange": {"minPer100g": 35.8, "maxPer100g": 39.9},
        "note": "無刺無腥，清蒸煮薑絲鱸魚湯方便",
        "imageUrl": "https://images.unsplash.com/photo-1534939561126-855b8675edd7?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "seafood-05",
        "name": "日本生食級干貝 3S (盒裝 1kg)",
        "category": "seafood",
        "subCategory": "冷凍水產",
        "pricingType": "fixed_package",
        "originalPrice": 1499,
        "discountAmount": 150,
        "discountEndDate": "2026-09-29",
        "packageSpec": "盒裝約 41-50顆 (1.0kg)",
        "totalWeightInGrams": 1000,
        "unitType": "g",
        "tagType": "weekly_sale",
        "historicalBenchmark": "historical_low",
        "storageType": "freeze",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "92144",
        "verifiedSource": "好市多水產部冷櫃",
        "historicalRange": {"minPer100g": 134.9, "maxPer100g": 159.0},
        "note": "生食刺身厚實鮮甜，乾煎雙面金黃即食",
        "imageUrl": "https://images.unsplash.com/photo-1559742811-822873691df8?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "seafood-06",
        "name": "ASC 冷凍吳郭魚片 (去骨去皮真空包)",
        "category": "seafood",
        "subCategory": "冷凍水產/魚排",
        "pricingType": "fixed_package",
        "originalPrice": 739,
        "discountAmount": 140,
        "discountEndDate": "2026-09-30",
        "packageSpec": "1.3kg (大包裝，單片獨立真空袋)",
        "totalWeightInGrams": 1300,
        "unitType": "g",
        "tagType": "weekly_sale",
        "historicalBenchmark": "historical_low",
        "storageType": "freeze",
        "priceSource": "online_catalog",
        "costcoItemNumber": "484596",
        "verifiedSource": "好市多官方本期優惠專頁 (Hot Buys)",
        "historicalRange": {"minPer100g": 46.1, "maxPer100g": 56.8},
        "isEstimatedPrice": False,
        "priceOrigin": "flyer_official",
        "note": "好市多熱賣 ASC 責任漁業認證冷凍吳郭魚片（台灣鯛魚片），去骨去皮無土味，1.3kg 官方原價 $739（每 100g 約 NT$ 56.8）！本期優惠現省 $140，特價只要 $599（每 100g NT$ 46.1），蒸煮乾煎超鮮嫩！",
        "imageUrl": "https://images.unsplash.com/photo-1534939561126-855b8675edd7?w=600&auto=format&fit=crop&q=80"
    },

    # 5. 生鮮蔬果 (Produce)
    {
        "id": "produce-01",
        "name": "紐西蘭陽光黃金奇異果 (原裝盒)",
        "category": "produce",
        "subCategory": "冷藏水果",
        "pricingType": "fixed_package",
        "originalPrice": 459,
        "discountAmount": 40,
        "discountEndDate": "2026-09-26",
        "packageSpec": "盒裝約 16-18顆 (2.2kg)",
        "totalWeightInGrams": 2200,
        "unitType": "g",
        "tagType": "weekly_sale",
        "historicalBenchmark": "historical_low",
        "storageType": "cold",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "87920",
        "verifiedSource": "好市多蔬果冷藏區",
        "historicalRange": {"minPer100g": 19.0, "maxPer100g": 22.5},
        "note": "高維他命C、香甜多汁，整箱比超市散買划算許多",
        "imageUrl": "https://images.unsplash.com/photo-1585059895524-72359e06133a?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "produce-02",
        "name": "台灣有機綜合水耕生菜 (生食級)",
        "category": "produce",
        "subCategory": "生鮮蔬菜",
        "pricingType": "fixed_package",
        "originalPrice": 199,
        "discountAmount": 0,
        "discountEndDate": None,
        "packageSpec": "大盒裝 (600g)",
        "totalWeightInGrams": 600,
        "unitType": "g",
        "tagType": "everyday_value",
        "historicalBenchmark": "standard",
        "storageType": "cold",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "128456",
        "verifiedSource": "蔬果冷藏低溫室",
        "historicalRange": {"minPer100g": 31.5, "maxPer100g": 35.0},
        "note": "免洗或微洗即食，製作生菜沙拉省時便利",
        "imageUrl": "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "produce-03",
        "name": "智利新鮮大粒藍莓 (大平盒裝)",
        "category": "produce",
        "subCategory": "冷藏水果",
        "pricingType": "fixed_package",
        "originalPrice": 269,
        "discountAmount": 0,
        "discountEndDate": None,
        "packageSpec": "平盒裝 (510g)",
        "totalWeightInGrams": 510,
        "unitType": "g",
        "tagType": "everyday_value",
        "historicalBenchmark": "standard",
        "storageType": "cold",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "76521",
        "verifiedSource": "好市多蔬果區",
        "historicalRange": {"minPer100g": 48.0, "maxPer100g": 58.0},
        "note": "花青素豐富，顆顆飽滿脆口",
        "imageUrl": "https://images.unsplash.com/photo-1498557850523-fd3d118b962e?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "produce-04",
        "name": "台灣產履歷小黃瓜 (大袋包裝)",
        "category": "produce",
        "subCategory": "生鮮蔬菜",
        "pricingType": "fixed_package",
        "originalPrice": 139,
        "discountAmount": 0,
        "discountEndDate": None,
        "packageSpec": "袋裝 (1.2kg)",
        "totalWeightInGrams": 1200,
        "unitType": "g",
        "tagType": "everyday_value",
        "historicalBenchmark": "standard",
        "storageType": "cold",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "108842",
        "verifiedSource": "好市多蔬果區",
        "historicalRange": {"minPer100g": 10.5, "maxPer100g": 13.5},
        "note": "涼拌、生吃、炒肉絲皆合適，量大清脆",
        "imageUrl": "https://images.unsplash.com/photo-1449300079323-02e209d9d3a6?w=600&auto=format&fit=crop&q=80"
    },

    # 6. 乳品與蛋 (Dairy)
    {
        "id": "dairy-01",
        "name": "Kirkland Signature 科克蘭全脂鮮乳",
        "category": "dairy",
        "subCategory": "冷藏乳飲",
        "pricingType": "fixed_package",
        "originalPrice": 269,
        "discountAmount": 0,
        "discountEndDate": None,
        "packageSpec": "1.89L x 2瓶 (共 3.78L)",
        "totalWeightInGrams": 3780,
        "unitType": "ml",
        "tagType": "everyday_value",
        "historicalBenchmark": "historical_low",
        "storageType": "cold",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "99960",
        "verifiedSource": "好市多常駐冷藏乳飲",
        "historicalRange": {"minPer100g": 6.8, "maxPer100g": 7.5},
        "note": "好市多長青熱門神物，每100ml不到 $7.2",
        "imageUrl": "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "dairy-02",
        "name": "Kirkland 科克蘭希臘式零脂優格",
        "category": "dairy",
        "subCategory": "冷藏發酵乳",
        "pricingType": "fixed_package",
        "originalPrice": 439,
        "discountAmount": 0,
        "discountEndDate": None,
        "packageSpec": "907g x 2桶入 (共 1814g)",
        "totalWeightInGrams": 1814,
        "unitType": "g",
        "tagType": "everyday_value",
        "historicalBenchmark": "standard",
        "storageType": "cold",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "888432",
        "verifiedSource": "今購百科最新價格",
        "historicalRange": {"minPer100g": 22.0, "maxPer100g": 25.5},
        "note": "超高蛋白、無糖厚實膏狀，健身早餐必備",
        "imageUrl": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "dairy-03",
        "name": "科克蘭科比傑克雙色乾酪條 (48入)",
        "category": "dairy",
        "subCategory": "乳酪起司",
        "pricingType": "fixed_package",
        "originalPrice": 499,
        "discountAmount": 70,
        "discountEndDate": "2026-09-26",
        "packageSpec": "24g x 48條裝 (共 1152g)",
        "totalWeightInGrams": 1152,
        "unitType": "g",
        "tagType": "weekly_sale",
        "historicalBenchmark": "historical_low",
        "storageType": "cold",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "57431",
        "verifiedSource": "好市多乳酪冷藏櫃",
        "historicalRange": {"minPer100g": 37.2, "maxPer100g": 43.3},
        "note": "獨立包裝，天然起司奶香濃郁零食",
        "imageUrl": "https://images.unsplash.com/photo-1589881133595-a3c085cb731d?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "dairy-04",
        "name": "石安牧場動福動態優質鮮蛋 (30顆入)",
        "category": "dairy",
        "subCategory": "生鮮蛋品",
        "pricingType": "fixed_package",
        "originalPrice": 389,
        "discountAmount": 0,
        "discountEndDate": None,
        "packageSpec": "盒裝 30顆 (約 1800g)",
        "totalWeightInGrams": 1800,
        "unitType": "g",
        "tagType": "everyday_value",
        "historicalBenchmark": "standard",
        "storageType": "cold",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "113254",
        "verifiedSource": "好市多雞蛋冷藏區",
        "historicalRange": {"minPer100g": 20.5, "maxPer100g": 23.5},
        "note": "友善動物福利認證，蛋黃挺拔香醇濃郁",
        "imageUrl": "https://images.unsplash.com/photo-1506976785307-8732e854ad03?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "dairy-05",
        "name": "Anchor 安佳純特級無鹽奶油條 (4入組)",
        "category": "dairy",
        "subCategory": "乳品油脂",
        "pricingType": "fixed_package",
        "originalPrice": 539,
        "discountAmount": 0,
        "discountEndDate": None,
        "packageSpec": "454g x 4條 (共 1816g)",
        "totalWeightInGrams": 1816,
        "unitType": "g",
        "tagType": "everyday_value",
        "historicalBenchmark": "standard",
        "storageType": "cold",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "103521",
        "verifiedSource": "好市多烘焙原料區",
        "historicalRange": {"minPer100g": 28.0, "maxPer100g": 31.5},
        "note": "紐西蘭純淨乳源，烘焙料理熱銷經典",
        "imageUrl": "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=600&auto=format&fit=crop&q=80"
    },

    # 7. 烘焙甜點 (Bakery)
    {
        "id": "bakery-01",
        "name": "好市多烘焙部綜合水煮貝果 (12入兩袋)",
        "category": "bakery",
        "subCategory": "現烤麵包",
        "pricingType": "fixed_package",
        "originalPrice": 259,
        "discountAmount": 0,
        "discountEndDate": None,
        "packageSpec": "6入 x 2袋任選 (約 1350g)",
        "totalWeightInGrams": 1350,
        "unitType": "g",
        "tagType": "everyday_value",
        "historicalBenchmark": "standard",
        "storageType": "room",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "102551",
        "verifiedSource": "好市多烘焙部現烤",
        "historicalRange": {"minPer100g": 17.5, "maxPer100g": 20.0},
        "note": "任選原味/藍莓/起司/洋蔥兩袋，冷凍保存烤後超Q彈",
        "imageUrl": "https://images.unsplash.com/photo-1585478259715-876a6a81ae08?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "bakery-02",
        "name": "法式烘焙迷你奶油可頌 (16入裝)",
        "category": "bakery",
        "subCategory": "現烤麵包",
        "pricingType": "fixed_package",
        "originalPrice": 219,
        "discountAmount": 30,
        "discountEndDate": "2026-09-25",
        "packageSpec": "透明大盒 16入 (約 400g)",
        "totalWeightInGrams": 400,
        "unitType": "g",
        "tagType": "weekly_sale",
        "historicalBenchmark": "historical_low",
        "storageType": "room",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "97223",
        "verifiedSource": "好市多現場特價標牌",
        "historicalRange": {"minPer100g": 47.3, "maxPer100g": 54.8},
        "note": "天然奶油酥皮香氣四溢，烤箱復熱酥脆逼人",
        "imageUrl": "https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "bakery-03",
        "name": "熟成多穀燕麥吐司 (2條家庭號)",
        "category": "bakery",
        "subCategory": "吐司麵包",
        "pricingType": "fixed_package",
        "originalPrice": 149,
        "discountAmount": 0,
        "discountEndDate": None,
        "packageSpec": "大條裝 2入 (共 1200g)",
        "totalWeightInGrams": 1200,
        "unitType": "g",
        "tagType": "everyday_value",
        "historicalBenchmark": "standard",
        "storageType": "room",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "123890",
        "verifiedSource": "好市多烘焙常駐品",
        "historicalRange": {"minPer100g": 11.5, "maxPer100g": 13.5},
        "note": "高纖燕麥穀粒飽足感強，早餐三明治好夥伴",
        "imageUrl": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "bakery-04",
        "name": "好市多經典提拉米蘇蛋糕 (大方盒)",
        "category": "bakery",
        "subCategory": "冷藏蛋糕",
        "pricingType": "fixed_package",
        "originalPrice": 329,
        "discountAmount": 0,
        "discountEndDate": None,
        "packageSpec": "家庭大方盒 (約 1100g)",
        "totalWeightInGrams": 1100,
        "unitType": "g",
        "tagType": "everyday_value",
        "historicalBenchmark": "standard",
        "storageType": "cold",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "98412",
        "verifiedSource": "好市多甜點冰櫃",
        "historicalRange": {"minPer100g": 28.0, "maxPer100g": 32.0},
        "note": "馬斯卡彭起司濃醇綿密，聚會派對必搶甜點",
        "imageUrl": "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=600&auto=format&fit=crop&q=80"
    },

    # 8. 熟食即食部 (Deli)
    {
        "id": "deli-01",
        "name": "好市多熟食部美式烤全雞 (現烤熱騰騰)",
        "category": "deli",
        "subCategory": "熟食部熱食",
        "pricingType": "fixed_package",
        "originalPrice": 189,
        "discountAmount": 0,
        "discountEndDate": None,
        "packageSpec": "保溫袋全雞 1入 (約 1.3kg)",
        "totalWeightInGrams": 1300,
        "unitType": "g",
        "tagType": "everyday_value",
        "historicalBenchmark": "historical_low",
        "storageType": "room",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "13988",
        "verifiedSource": "熟食部現烤標價牌",
        "historicalRange": {"minPer100g": 13.5, "maxPer100g": 14.5},
        "note": "熟食即食，CP值破表的常駐肉品王者",
        "imageUrl": "https://images.unsplash.com/photo-1598103442097-8b74394b95c6?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "deli-02",
        "name": "熟食部經典凱薩雞肉沙拉 (附特調醬汁)",
        "category": "deli",
        "subCategory": "熟食沙拉",
        "pricingType": "fixed_package",
        "originalPrice": 189,
        "discountAmount": 0,
        "discountEndDate": None,
        "packageSpec": "透明大圓盒 (約 800g)",
        "totalWeightInGrams": 800,
        "unitType": "g",
        "tagType": "everyday_value",
        "historicalBenchmark": "standard",
        "storageType": "cold",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "17855",
        "verifiedSource": "好市多熟食冷藏櫃",
        "historicalRange": {"minPer100g": 22.0, "maxPer100g": 25.0},
        "note": "羅美生菜、厚切雞胸肉與帕瑪森乾酪絲",
        "imageUrl": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "deli-03",
        "name": "好市多熟食部 18吋美式經典起司披薩",
        "category": "deli",
        "subCategory": "熟食部熱食",
        "pricingType": "fixed_package",
        "originalPrice": 300,
        "discountAmount": 0,
        "discountEndDate": None,
        "packageSpec": "超大18吋圓盤 (約 1800g)",
        "totalWeightInGrams": 1800,
        "unitType": "g",
        "tagType": "everyday_value",
        "historicalBenchmark": "historical_low",
        "storageType": "room",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "14210",
        "verifiedSource": "熟食餐飲點餐檯",
        "historicalRange": {"minPer100g": 15.5, "maxPer100g": 17.5},
        "note": "派對聚會巨無霸披薩，濃郁牽絲起司",
        "imageUrl": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "deli-04",
        "name": "熟食部德國脆皮豬腳佐酸菜",
        "category": "deli",
        "subCategory": "熟食部熱食",
        "pricingType": "fixed_package",
        "originalPrice": 499,
        "discountAmount": 60,
        "discountEndDate": "2026-09-28",
        "packageSpec": "大盒切塊裝 (約 1.4kg)",
        "totalWeightInGrams": 1400,
        "unitType": "g",
        "tagType": "weekly_sale",
        "historicalBenchmark": "historical_low",
        "storageType": "room",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "119852",
        "verifiedSource": "今購百科最新特價實拍照",
        "historicalRange": {"minPer100g": 31.4, "maxPer100g": 37.5},
        "note": "外皮酥脆肉質軟嫩，附經典德式酸菜與黃芥末",
        "imageUrl": "https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop&q=80"
    },

    # 9. 零食堅果 (Snacks)
    {
        "id": "snacks-01",
        "name": "Kirkland 科克蘭特選無調味綜合堅果",
        "category": "snacks",
        "subCategory": "堅果零食",
        "pricingType": "fixed_package",
        "originalPrice": 599,
        "discountAmount": 60,
        "discountEndDate": "2026-09-27",
        "packageSpec": "原裝透明大方桶 (1.13kg)",
        "totalWeightInGrams": 1130,
        "unitType": "g",
        "tagType": "weekly_sale",
        "historicalBenchmark": "historical_low",
        "storageType": "room",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "75037",
        "verifiedSource": "好市多堅果零食區",
        "historicalRange": {"minPer100g": 47.7, "maxPer100g": 54.0},
        "note": "腰果、杏仁、胡桃、夏威夷豆，無鹽低溫烘焙健康首選",
        "imageUrl": "https://images.unsplash.com/photo-1508746829417-e6f548d8d6ed?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "snacks-02",
        "name": "韓味不二人氣海苔酥 (白飯殺手)",
        "category": "snacks",
        "subCategory": "休閒海苔",
        "pricingType": "fixed_package",
        "originalPrice": 399,
        "discountAmount": 50,
        "discountEndDate": "2026-09-28",
        "packageSpec": "夾鏈袋 3包組 (共 300g)",
        "totalWeightInGrams": 300,
        "unitType": "g",
        "tagType": "weekly_sale",
        "historicalBenchmark": "historical_low",
        "storageType": "room",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "118334",
        "verifiedSource": "好市多進口休閒零食",
        "historicalRange": {"minPer100g": 116.3, "maxPer100g": 133.0},
        "note": "香油白芝麻翻炒，拌飯捏飯糰秒殺",
        "imageUrl": "https://images.unsplash.com/photo-1508746829417-e6f548d8d6ed?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "snacks-03",
        "name": "Lay's 樂事經典原味洋芋片大分享箱",
        "category": "snacks",
        "subCategory": "洋芋片餅乾",
        "pricingType": "fixed_package",
        "originalPrice": 159,
        "discountAmount": 0,
        "discountEndDate": None,
        "packageSpec": "巨無霸袋裝 (425g)",
        "totalWeightInGrams": 425,
        "unitType": "g",
        "tagType": "everyday_value",
        "historicalBenchmark": "standard",
        "storageType": "room",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "58714",
        "verifiedSource": "好市多餅乾洋芋片區",
        "historicalRange": {"minPer100g": 35.0, "maxPer100g": 39.0},
        "note": "看電影聚會派對必買，特濃馬鈴薯原味",
        "imageUrl": "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "snacks-04",
        "name": "雀巢 KitKat 迷你黑巧克力 (大袋裝)",
        "category": "snacks",
        "subCategory": "巧克力甜食",
        "pricingType": "fixed_package",
        "originalPrice": 429,
        "discountAmount": 60,
        "discountEndDate": "2026-09-29",
        "packageSpec": "分享大袋裝 (840g 約 70入)",
        "totalWeightInGrams": 840,
        "unitType": "g",
        "tagType": "black_card",
        "historicalBenchmark": "historical_low",
        "storageType": "room",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "124319",
        "verifiedSource": "好市多糖果巧克力區",
        "historicalRange": {"minPer100g": 43.9, "maxPer100g": 52.0},
        "note": "濃郁微苦不甜膩，威化酥脆下午茶點心",
        "imageUrl": "https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?w=600&auto=format&fit=crop&q=80"
    },

    # 10. 米麵調味乾貨 (Pantry)
    {
        "id": "pantry-01",
        "name": "關山台梗九號米 (花東產優質米)",
        "category": "pantry",
        "subCategory": "米糧乾貨",
        "pricingType": "fixed_package",
        "originalPrice": 699,
        "discountAmount": 70,
        "discountEndDate": "2026-09-27",
        "packageSpec": "厚磅家庭袋裝 (9.0kg)",
        "totalWeightInGrams": 9000,
        "unitType": "g",
        "tagType": "weekly_sale",
        "historicalBenchmark": "historical_low",
        "storageType": "room",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "86420",
        "verifiedSource": "好市多米糧乾貨區",
        "historicalRange": {"minPer100g": 6.9, "maxPer100g": 8.0},
        "note": "米粒飽滿Q黏，冷飯做壽司飯糰依然香甜",
        "imageUrl": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "pantry-02",
        "name": "Barilla 百味來義大利直麵 (6盒裝)",
        "category": "pantry",
        "subCategory": "義大利麵食",
        "pricingType": "fixed_package",
        "originalPrice": 319,
        "discountAmount": 0,
        "discountEndDate": None,
        "packageSpec": "500g x 6盒組 (共 3000g)",
        "totalWeightInGrams": 3000,
        "unitType": "g",
        "tagType": "everyday_value",
        "historicalBenchmark": "standard",
        "storageType": "room",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "93455",
        "verifiedSource": "好市多進口米麵專區",
        "historicalRange": {"minPer100g": 9.8, "maxPer100g": 11.2},
        "note": "經典杜蘭小麥粉壓製，彈牙勁道不易煮爛",
        "imageUrl": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "pantry-03",
        "name": "Kirkland 科克蘭有機特級冷壓初榨橄欖油",
        "category": "pantry",
        "subCategory": "料理食用油",
        "pricingType": "fixed_package",
        "originalPrice": 549,
        "discountAmount": 0,
        "discountEndDate": None,
        "packageSpec": "大容量深色防光瓶 (2.0L)",
        "totalWeightInGrams": 1820,
        "unitType": "ml",
        "tagType": "everyday_value",
        "historicalBenchmark": "historical_low",
        "storageType": "room",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "103212",
        "verifiedSource": "好市多食用油專區",
        "historicalRange": {"minPer100g": 27.5, "maxPer100g": 31.0},
        "note": "第一道冷壓萃取，涼拌生飲或中小火烹飪皆宜",
        "imageUrl": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "pantry-04",
        "name": "桂格即食大燕麥片 (原粒壓製家庭號)",
        "category": "pantry",
        "subCategory": "燕麥穀物",
        "pricingType": "fixed_package",
        "originalPrice": 389,
        "discountAmount": 50,
        "discountEndDate": "2026-09-28",
        "packageSpec": "箱裝大袋 (3.0kg)",
        "totalWeightInGrams": 3000,
        "unitType": "g",
        "tagType": "weekly_sale",
        "historicalBenchmark": "historical_low",
        "storageType": "room",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "79201",
        "verifiedSource": "好市多早餐穀物區",
        "historicalRange": {"minPer100g": 11.3, "maxPer100g": 13.0},
        "note": "國家健康食品認證，降膽固醇增肌減脂常備",
        "imageUrl": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600&auto=format&fit=crop&q=80"
    },

    # 11. 飲料咖啡酒類 (Beverages)
    {
        "id": "beverages-01",
        "name": "Starbucks 星巴克早餐綜合咖啡豆 (中烘焙)",
        "category": "beverages",
        "subCategory": "精品咖啡豆",
        "pricingType": "fixed_package",
        "originalPrice": 789,
        "discountAmount": 100,
        "discountEndDate": "2026-09-28",
        "packageSpec": "大銀袋 (1.13kg)",
        "totalWeightInGrams": 1130,
        "unitType": "g",
        "tagType": "weekly_sale",
        "historicalBenchmark": "historical_low",
        "storageType": "room",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "117869",
        "verifiedSource": "好市多咖啡專區現場折讓",
        "historicalRange": {"minPer100g": 61.0, "maxPer100g": 72.0},
        "note": "清爽明亮帶有柑橘香氣，美式手沖必備",
        "imageUrl": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "beverages-02",
        "name": "San Pellegrino 聖沛黎洛天然氣泡礦泉水",
        "category": "beverages",
        "subCategory": "氣泡礦泉水",
        "pricingType": "fixed_package",
        "originalPrice": 599,
        "discountAmount": 80,
        "discountEndDate": "2026-09-27",
        "packageSpec": "500ml x 24瓶 (箱裝 12L)",
        "totalWeightInGrams": 12000,
        "unitType": "ml",
        "tagType": "weekly_sale",
        "historicalBenchmark": "historical_low",
        "storageType": "room",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "68523",
        "verifiedSource": "好市多水飲專區本週特賣",
        "historicalRange": {"minPer100g": 4.3, "maxPer100g": 5.2},
        "note": "義大利阿爾卑斯山純淨水源，氣泡細緻搭檸檬無敵",
        "imageUrl": "https://images.unsplash.com/photo-1548839140-29a749e1bc4e?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "beverages-03",
        "name": "純在冷壓鮮榨芭樂檸檬綠茶 (2瓶入)",
        "category": "beverages",
        "subCategory": "冷藏鮮果汁",
        "pricingType": "fixed_package",
        "originalPrice": 199,
        "discountAmount": 0,
        "discountEndDate": None,
        "packageSpec": "1.2L x 2瓶 (共 2400ml)",
        "totalWeightInGrams": 2400,
        "unitType": "ml",
        "tagType": "everyday_value",
        "historicalBenchmark": "standard",
        "storageType": "cold",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "121894",
        "verifiedSource": "好市多冷藏飲品專區",
        "historicalRange": {"minPer100g": 7.8, "maxPer100g": 8.8},
        "note": "HPP超高壓低溫殺菌，喝得到芭樂果泥纖維爆紅款",
        "imageUrl": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "beverages-04",
        "name": "Kirkland 科克蘭有機純椰子水 (6瓶箱裝)",
        "category": "beverages",
        "subCategory": "機能果汁",
        "pricingType": "fixed_package",
        "originalPrice": 399,
        "discountAmount": 0,
        "discountEndDate": None,
        "packageSpec": "1.0L x 6瓶 (共 6000ml)",
        "totalWeightInGrams": 6000,
        "unitType": "ml",
        "tagType": "everyday_value",
        "historicalBenchmark": "standard",
        "storageType": "room",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "109845",
        "verifiedSource": "好市多飲品區",
        "historicalRange": {"minPer100g": 6.2, "maxPer100g": 6.9},
        "note": "非濃縮還原純天然電解質補給，運動補水首選",
        "imageUrl": "https://images.unsplash.com/photo-1548839140-29a749e1bc4e?w=600&auto=format&fit=crop&q=80"
    },

    # 12. 冷凍食品 (Frozen)
    {
        "id": "frozen-01",
        "name": "卜蜂冷凍日式鹽烤雞肉串 (30支)",
        "category": "frozen",
        "subCategory": "冷凍熟食調理",
        "pricingType": "fixed_package",
        "originalPrice": 499,
        "discountAmount": 80,
        "discountEndDate": "2026-09-27",
        "packageSpec": "30支裝盒 (900g)",
        "totalWeightInGrams": 900,
        "unitType": "g",
        "tagType": "weekly_sale",
        "historicalBenchmark": "historical_low",
        "storageType": "freeze",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "115982",
        "verifiedSource": "好市多冷凍食品特價標牌",
        "historicalRange": {"minPer100g": 46.5, "maxPer100g": 55.4},
        "note": "氣炸鍋加熱 10 分鐘，居酒屋風味宵夜必備",
        "imageUrl": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "frozen-02",
        "name": "Kirkland 冷凍野生三種綜合莓果",
        "category": "frozen",
        "subCategory": "冷凍水果",
        "pricingType": "fixed_package",
        "originalPrice": 519,
        "discountAmount": 0,
        "discountEndDate": None,
        "packageSpec": "大夾鏈袋 (1.81kg)",
        "totalWeightInGrams": 1810,
        "unitType": "g",
        "tagType": "everyday_value",
        "historicalBenchmark": "standard",
        "storageType": "freeze",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "722573",
        "verifiedSource": "好市多冷凍水果專區",
        "historicalRange": {"minPer100g": 27.0, "maxPer100g": 31.0},
        "note": "黑莓、藍莓、覆盆莓，打優格果昔極佳",
        "imageUrl": "https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "frozen-03",
        "name": "奇美 冷凍老饕鮮肉包 (16入裝)",
        "category": "frozen",
        "subCategory": "冷凍麵食點心",
        "pricingType": "fixed_package",
        "originalPrice": 349,
        "discountAmount": 40,
        "discountEndDate": "2026-09-28",
        "packageSpec": "120g x 16入 (共 1920g)",
        "totalWeightInGrams": 1920,
        "unitType": "g",
        "tagType": "weekly_sale",
        "historicalBenchmark": "historical_low",
        "storageType": "freeze",
        "priceSource": "online_catalog",
        "costcoItemNumber": "171168",
        "verifiedSource": "好市多線上即時商品",
        "historicalRange": {"minPer100g": 16.1, "maxPer100g": 18.2},
        "note": "好市多線上即時商品 (#171168)，皮Q肉鮮爆汁早餐首選",
        "imageUrl": "https://images.unsplash.com/photo-1563245372-f21724e3856d?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "frozen-04",
        "name": "陳品 冷凍豬肉水餃 (大包裝 180顆)",
        "category": "frozen",
        "subCategory": "冷凍麵點",
        "pricingType": "fixed_package",
        "originalPrice": 379,
        "discountAmount": 0,
        "discountEndDate": None,
        "packageSpec": "18g x 180顆 (共 3240g)",
        "totalWeightInGrams": 3240,
        "unitType": "g",
        "tagType": "everyday_value",
        "historicalBenchmark": "standard",
        "storageType": "freeze",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "153261",
        "verifiedSource": "好市多冷凍麵點區",
        "historicalRange": {"minPer100g": 11.2, "maxPer100g": 12.5},
        "note": "好市多線上即時商品 (#153261)，平均一顆才 $2.1",
        "imageUrl": "https://images.unsplash.com/photo-1496116218417-1a781b1c416c?w=600&auto=format&fit=crop&q=80"
    },
    {
        "id": "frozen-05",
        "name": "哈根達斯 Häagen-Dazs 經典冰淇淋品脫迷你杯組",
        "category": "frozen",
        "subCategory": "冷凍冰品",
        "pricingType": "fixed_package",
        "originalPrice": 799,
        "discountAmount": 120,
        "discountEndDate": "2026-09-30",
        "packageSpec": "100ml x 10入 (共 1000ml)",
        "totalWeightInGrams": 1000,
        "unitType": "ml",
        "tagType": "black_card",
        "historicalBenchmark": "historical_low",
        "storageType": "freeze",
        "priceSource": "warehouse_only",
        "costcoItemNumber": "119284",
        "verifiedSource": "好市多黑鑽卡專屬優惠",
        "historicalRange": {"minPer100g": 67.9, "maxPer100g": 79.9},
        "note": "草莓、香草、夏威夷果仁人氣口味混搭，黑鑽卡強檔現省",
        "imageUrl": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=600&auto=format&fit=crop&q=80"
    }
]

def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        sub_category TEXT,
        pricing_type TEXT DEFAULT 'fixed_package',
        price_per_kg REAL,
        original_price INTEGER NOT NULL,
        discount_amount INTEGER DEFAULT 0,
        discount_end_date TEXT,
        package_spec TEXT NOT NULL,
        total_weight_grams INTEGER NOT NULL,
        unit_type TEXT DEFAULT 'g',
        tag_type TEXT DEFAULT 'none',
        historical_benchmark TEXT DEFAULT 'standard',
        storage_type TEXT DEFAULT 'cold',
        price_source TEXT DEFAULT 'warehouse_only',
        costco_item_number TEXT,
        verified_source TEXT,
        historical_range_min REAL,
        historical_range_max REAL,
        note TEXT,
        image_url TEXT,
        local_image_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Ensure all columns exist in case table was created previously with older schema
    existing_cols = [c[1] for c in cursor.execute("PRAGMA table_info(products)").fetchall()]
    new_cols = [
        ("pricing_type", "TEXT DEFAULT 'fixed_package'"),
        ("price_per_kg", "REAL"),
        ("price_source", "TEXT DEFAULT 'warehouse_only'"),
        ("costco_item_number", "TEXT"),
        ("verified_source", "TEXT"),
        ("historical_range_min", "REAL"),
        ("historical_range_max", "REAL"),
        ("is_estimated_price", "INTEGER DEFAULT 0"),
        ("price_origin", "TEXT DEFAULT 'store_tag'")
    ]
    for col_name, col_def in new_cols:
        if col_name not in existing_cols:
            cursor.execute(f"ALTER TABLE products ADD COLUMN {col_name} {col_def}")
            print(f"[DB] Added column {col_name} to products table.")

    conn.commit()
    print(f"[DB] SQLite database initialized at {DB_PATH}")

    from scripts.costco_official_scraper import OFFICIAL_PROMOTIONS_DATA

    # Combine INITIAL_PRODUCTS and OFFICIAL_PROMOTIONS_DATA (official scraped items take precedence)
    all_products_dict = {p["id"]: dict(p) for p in INITIAL_PRODUCTS}
    for promo in OFFICIAL_PROMOTIONS_DATA:
        all_products_dict[promo["id"]] = dict(promo)
    all_products = list(all_products_dict.values())

    # Upsert products
    for p in all_products:
        local_img = p.get("localImage", f"/images/products/{p['id']}.jpg")
        hr = p.get("historicalRange")
        hr_min = hr["minPer100g"] if hr else None
        hr_max = hr["maxPer100g"] if hr else None
        is_est = 1 if (p.get("isEstimatedPrice", False) or p.get("pricingType") == "by_weight") else 0
        price_orig = p.get("priceOrigin", "calculated_by_weight" if p.get("pricingType") == "by_weight" else "store_tag")

        cursor.execute("""
        INSERT INTO products (
            id, name, category, sub_category, pricing_type, price_per_kg, original_price,
            discount_amount, discount_end_date, package_spec, total_weight_grams,
            unit_type, tag_type, historical_benchmark, storage_type, price_source,
            costco_item_number, verified_source, historical_range_min, historical_range_max,
            is_estimated_price, price_origin, note, image_url, local_image_path, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            category=excluded.category,
            sub_category=excluded.sub_category,
            pricing_type=excluded.pricing_type,
            price_per_kg=excluded.price_per_kg,
            original_price=excluded.original_price,
            discount_amount=excluded.discount_amount,
            discount_end_date=excluded.discount_end_date,
            package_spec=excluded.package_spec,
            total_weight_grams=excluded.total_weight_grams,
            unit_type=excluded.unit_type,
            tag_type=excluded.tag_type,
            historical_benchmark=excluded.historical_benchmark,
            storage_type=excluded.storage_type,
            price_source=excluded.price_source,
            costco_item_number=excluded.costco_item_number,
            verified_source=excluded.verified_source,
            historical_range_min=excluded.historical_range_min,
            historical_range_max=excluded.historical_range_max,
            is_estimated_price=excluded.is_estimated_price,
            price_origin=excluded.price_origin,
            note=excluded.note,
            image_url=excluded.image_url,
            local_image_path=excluded.local_image_path,
            updated_at=CURRENT_TIMESTAMP
        """, (
            p["id"], p["name"], p["category"], p.get("subCategory"),
            p.get("pricingType", "fixed_package"), p.get("pricePerKg"), p["originalPrice"],
            p.get("discountAmount", 0), p.get("discountEndDate"), p["packageSpec"],
            p["totalWeightInGrams"], p.get("unitType", "g"), p.get("tagType", "none"),
            p.get("historicalBenchmark", "standard"), p.get("storageType", "cold"),
            p.get("priceSource", "warehouse_only"), p.get("costcoItemNumber"),
            p.get("verifiedSource"), hr_min, hr_max,
            is_est, price_orig,
            p.get("note", ""), p.get("imageUrl", p.get("cdnImage", "")), local_img
        ))
    conn.commit()
    conn.close()
    print(f"[DB] Synced {len(all_products)} items (including official scraped promotions) into SQLite table 'products'.")

# 好市多官方優惠專頁 (Hot-Buys / 會員皮夾 / 即時特價目錄) 特價情報集
OFFICIAL_FLYER_PROMOTIONS = [
    {
        "costcoItemNumber": "484596",
        "name": "ASC 冷凍吳郭魚片 (去骨去皮真空包)",
        "flyerOriginalPrice": 739,
        "discountAmount": 140,
        "discountEndDate": "2026-09-30",
        "source": "好市多官方本期優惠專頁 (Hot Buys)"
    },
    {
        "costcoItemNumber": "67404",
        "name": "美國特選嫩肩里肌真空包 (Choice)",
        "flyerOriginalPrice": 1369,
        "discountAmount": 150,
        "discountEndDate": "2026-09-27",
        "source": "好市多本期特惠專頁"
    },
    {
        "costcoItemNumber": "89104",
        "name": "空運挪威冷藏鮭魚切片 (生鮮)",
        "flyerOriginalPrice": 989,
        "discountAmount": 110,
        "discountEndDate": "2026-09-27",
        "source": "好市多海鮮專案折讓"
    },
    {
        "costcoItemNumber": "115982",
        "name": "卜蜂冷凍日式鹽烤雞肉串 (30支)",
        "flyerOriginalPrice": 499,
        "discountAmount": 80,
        "discountEndDate": "2026-09-27",
        "source": "好市多冷凍特賣專頁"
    },
    {
        "costcoItemNumber": "68523",
        "name": "San Pellegrino 聖沛黎洛天然氣泡礦泉水",
        "flyerOriginalPrice": 599,
        "discountAmount": 80,
        "discountEndDate": "2026-09-27",
        "source": "好市多水飲促銷專頁"
    },
    {
        "costcoItemNumber": "117869",
        "name": "Starbucks 星巴克早餐綜合咖啡豆 (中烘焙)",
        "flyerOriginalPrice": 789,
        "discountAmount": 100,
        "discountEndDate": "2026-09-28",
        "source": "好市多咖啡特惠專頁"
    },
    {
        "costcoItemNumber": "86420",
        "name": "關山台梗九號米 (花東產優質米)",
        "flyerOriginalPrice": 699,
        "discountAmount": 70,
        "discountEndDate": "2026-09-27",
        "source": "好市多本期特惠專頁"
    },
    {
        "costcoItemNumber": "124981",
        "name": "熟凍加拿大松葉蟹鉗腳",
        "flyerOriginalPrice": 1499,
        "discountAmount": 200,
        "discountEndDate": "2026-09-30",
        "source": "黑鑽卡專屬優惠專頁"
    },
    {
        "costcoItemNumber": "171168",
        "name": "奇美 冷凍老饕鮮肉包 (16入裝)",
        "flyerOriginalPrice": 349,
        "discountAmount": 40,
        "discountEndDate": "2026-09-28",
        "source": "好市多線上即時促銷"
    },
    {
        "costcoItemNumber": "92144",
        "name": "日本生食級干貝 3S (盒裝 1kg)",
        "flyerOriginalPrice": 1499,
        "discountAmount": 150,
        "discountEndDate": "2026-09-29",
        "source": "好市多水產部冷櫃"
    }
]

def sync_official_promotions(promotions=None):
    """
    好市多官方優惠專頁自動比對與原價覆蓋管線：
    若商品在好市多最新特價專頁 (Hot Buys) 出現：
    1. 自動識別該商品是否為計算/預估原價 (is_estimated_price = 1)
    2. 自動將原價 (original_price) 替換為好市多優惠專頁刊登之【真實官方正式原價】
    3. 自動同步折價金額 (discount_amount)、活動截止日 (discount_end_date)
    4. 將 price_origin 標記為 'flyer_official'，is_estimated_price 改為 0
    5. 自動更新 SQLite 並重新導出至 mockProducts.ts 與 products.json
    """
    if promotions is None:
        promotions = OFFICIAL_FLYER_PROMOTIONS

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    updated_count = 0
    print(f"\n[PROMO-SYNC] Scanning {len(promotions)} official promotion deals against local database...")

    for promo in promotions:
        item_no = str(promo["costcoItemNumber"])
        flyer_orig_price = promo["flyerOriginalPrice"]
        discount = promo["discountAmount"]
        end_date = promo.get("discountEndDate")
        source = promo.get("source", "好市多官方本期優惠專頁 (Hot Buys)")

        cursor.execute("SELECT id, name, original_price, is_estimated_price, price_origin FROM products WHERE costco_item_number = ?", (item_no,))
        row = cursor.fetchone()

        if row:
            pid, pname, old_orig, is_est, old_origin = row
            status_desc = "估算價格替換為官方正式原價" if is_est else "官方正式原價與折讓確認"
            cursor.execute("""
                UPDATE products 
                SET original_price = ?,
                    discount_amount = ?,
                    discount_end_date = ?,
                    is_estimated_price = 0,
                    price_origin = 'flyer_official',
                    verified_source = ?,
                    tag_type = 'weekly_sale',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (flyer_orig_price, discount, end_date, source, pid))
            print(f"  [UPDATED] #{item_no} {pname}: {status_desc} -> 原價 NT$ {flyer_orig_price} (現折 NT$ {discount})")
            updated_count += 1
        else:
            print(f"  [NOTICE] Promo item #{item_no} ({promo['name']}) not found in current catalog.")

    conn.commit()
    conn.close()
    print(f"[PROMO-SYNC] Successfully synced {updated_count} items with official flyer prices.\n")

def download_images():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, image_url FROM products")
    rows = cursor.fetchall()
    conn.close()

    print(f"[IMG] Starting image download check for {len(rows)} products into {IMAGES_DIR}...")
    success_count = 0
    for pid, name, url in rows:
        dest = os.path.join(IMAGES_DIR, f"{pid}.jpg")
        if os.path.exists(dest) and os.path.getsize(dest) > 1000:
            success_count += 1
            continue

        if not url:
            continue

        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                data = resp.read()
                with open(dest, "wb") as f:
                    f.write(data)
                print(f"  [OK] Downloaded {pid}.jpg ({len(data)} bytes)")
                success_count += 1
                time.sleep(0.1)
        except Exception as e:
            print(f"  [FAIL] Failed to download image for {pid}: {e}")

    print(f"[IMG] Finished image downloads: {success_count}/{len(rows)} available in {IMAGES_DIR}")

def export_to_frontend():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY category, original_price")
    rows = cursor.fetchall()
    conn.close()

    items = []
    for r in rows:
        item = {
            "id": r["id"],
            "name": r["name"],
            "category": r["category"],
            "subCategory": r["sub_category"],
            "pricingType": r["pricing_type"],
            "originalPrice": r["original_price"],
            "discountAmount": r["discount_amount"],
            "discountEndDate": r["discount_end_date"],
            "packageSpec": r["package_spec"],
            "totalWeightInGrams": r["total_weight_grams"],
            "unitType": r["unit_type"],
            "tagType": r["tag_type"],
            "historicalBenchmark": r["historical_benchmark"],
            "storageType": r["storage_type"],
            "note": r["note"],
            "imageUrl": r["image_url"],
            "localImage": r["local_image_path"],
            "priceSource": r["price_source"]
        }
        if r["price_per_kg"] is not None:
            item["pricePerKg"] = r["price_per_kg"]
        if r["costco_item_number"] is not None:
            item["costcoItemNumber"] = r["costco_item_number"]
        if r["verified_source"] is not None:
            item["verifiedSource"] = r["verified_source"]
        if "is_estimated_price" in r.keys() and r["is_estimated_price"] is not None:
            item["isEstimatedPrice"] = bool(r["is_estimated_price"])
        if "price_origin" in r.keys() and r["price_origin"] is not None:
            item["priceOrigin"] = r["price_origin"]
        if r["historical_range_min"] is not None and r["historical_range_max"] is not None:
            item["historicalRange"] = {
                "minPer100g": r["historical_range_min"],
                "maxPer100g": r["historical_range_max"]
            }
        items.append(item)

    # Export to public/data/products.json
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"[EXPORT] Saved {len(items)} items to JSON at {OUTPUT_JSON}")

    # Export to src/data/mockProducts.ts
    ts_code = f'''import {{ Product }} from '../types/product';

/**
 * 本資料庫由 scripts/costco_sync.py 自動由 SQLite (costco_products.db) 同步產出
 * 包含好市多官方優惠專頁 (Hot Buys) 驗證原價、生鮮每公斤牌價與 100g 基準換算
 */
export const MOCK_PRODUCTS: Product[] = {json.dumps(items, ensure_ascii=False, indent=2)};
'''
    with open(OUTPUT_TS, "w", encoding="utf-8") as f:
        f.write(ts_code)
    print(f"[EXPORT] Updated TypeScript dataset at {OUTPUT_TS}")

if __name__ == "__main__":
    print("=== Costco Scraper, Image Downloader & SQLite Sync Pipeline ===")
    from scripts.costco_official_scraper import download_official_images
    download_official_images()
    init_database()
    sync_official_promotions()
    export_to_frontend()
    print("=== All Sync Tasks Completed Successfully! ===")
