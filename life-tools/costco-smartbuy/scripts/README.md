# Costco 100g 比價系統 - 爬蟲與資料管線架構說明

本專案所有的資料管線均符合 [AGENTS.md](file:///c:/Binson/Mytools/Python/SideProject/Costco/AGENTS.md) 規範，支援標準旗標（`--force`、`--step`、`--from-step`、`--dry-run`、`--reset`）， inter-step 皆以沙箱檔案隔離傳遞，保證冪等性與中斷續跑。

---

## 📁 資料管線清單

### 1. 特價與促銷管線 (`scripts/promo_pipeline/`)
- **用途**：每週定時更新好市多線上優惠、每週特價（Hot Buys）、會員優惠券與黑鑽卡折價。
- **主執行檔**：`python scripts/promo_pipeline/run_promo_pipeline.py`
- **常用指令**：
  ```bash
  # 強制重新執行全管線
  python scripts/promo_pipeline/run_promo_pipeline.py --force
  ```

### 2. 賣場限定／Uber Eats 熱銷生鮮管線 (`scripts/warehouse_pipeline/`)
- **用途**：採集好市多實體門市限定商品（WH08）與 Uber Eats 熱銷生鮮肉品（如清雞腿真空包 `#118583`、特選牛排、熟食壽司等），並對接今購百科實體標牌。
- **主執行檔**：`python scripts/warehouse_pipeline/run_warehouse_pipeline.py`
- **常用指令**：
  ```bash
  python scripts/warehouse_pipeline/run_warehouse_pipeline.py --force
  ```

### 3. 今購網實體標牌比對修正管線 (`scripts/daybuy_pipeline/`)
- **用途**：批次搜尋今購百科（Daybuy.tw）門市實拍標價牌與專櫃圖片，校正真實原價與歷史價格區間。
- **主執行檔**：`python scripts/daybuy_pipeline/run_daybuy_pipeline.py`
- **常用指令**：
  ```bash
  python scripts/daybuy_pipeline/run_daybuy_pipeline.py --force
  ```

### 4. 食品大類全目錄管線 (`scripts/c8_pipeline/`)
- **用途**：好市多全食物大類（`c/8`）深層遞迴採集。
- **主執行檔**：`python scripts/c8_pipeline/run_c8_pipeline.py`

---

## 🛠️ 維護與輔助工具

| 檔案 | 用途 |
|---|---|
| `scripts/deduplicate_products.py` | 全庫 SKU 唯一性校驗與重複整併工具（防止 `costco-{sku}` 與 `{sku}` 重複） |
| `scripts/add_product.py` | 終端機手動單筆新增／修正商品 CLI 工具 |
| `scripts/archive/` | 早期探索性腳本與原始暫存紀錄封存區 |

---

## 🚀 常用 NPM 捷徑指令

在專案根目錄下可直接透過 `npm run <command>` 執行：

```bash
# 開發伺服器（支援區域網路手機連線）
npm run dev

# 生產環境編譯打包檢查
npm run build

# 更新當週促銷特價
npm run update-promos

# 更新門市限定生鮮
npm run update-warehouse

# 一鍵：更新特價並自動重新發佈上線 (Vercel)
npm run update-and-deploy

# 發佈至 Vercel 生產環境
npm run deploy
```
