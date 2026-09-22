export type ProductCategory = 
  | 'beef' 
  | 'chicken' 
  | 'pork' 
  | 'seafood' 
  | 'produce'    // 生鮮蔬果
  | 'dairy'      // 乳製品與蛋
  | 'bakery'     // 烘焙麵包甜點
  | 'deli'       // 熟食即食部
  | 'snacks'     // 零食堅果
  | 'pantry'     // 米麵調味乾貨
  | 'beverages'  // 飲料咖啡酒類
  | 'frozen'     // 冷凍食品
  | 'other';

export type TagType = 'weekly_sale' | 'black_card' | 'everyday_value' | 'none';

export type HistoricalBenchmark = 'historical_low' | 'standard' | 'above_average';

export type PricingType = 'by_weight' | 'fixed_package'; // 秤重計價 (看公斤牌) vs 固定大包裝定價

export type PriceOrigin = 'flyer_official' | 'calculated_by_weight' | 'store_tag';

export interface Product {
  id: string;
  name: string;
  category: ProductCategory;
  subCategory?: string | null;
  pricingType?: PricingType;        // 秤重計價 (by_weight) 還是 固定包裝 (fixed_package)
  pricePerKg?: number;              // 若為秤重商品：真實每公斤牌價 NT$/kg (核心真實基準)
  originalPrice: number;            // 原總價 NT$ (固定包裝為定價；秤重商品為預估單包總價)
  isEstimatedPrice?: boolean;       // 是否為依重量估算之單包原價 (true: 依包重換算, false: 官方優惠專頁正式原價)
  priceOrigin?: PriceOrigin;        // 價格來源 (flyer_official: 好市多優惠專頁官方原價; calculated_by_weight: 每公斤牌價估算; store_tag: 現場標牌)
  discountAmount?: number;          // 特價折讓金額 NT$
  discountEndDate?: string | null;  // 特價截止日 (例如 '2026-09-27')
  packageSpec: string;              // 包裝規格描述 (例如 '2.7kg (約6包)')
  totalWeightInGrams: number;       // 總公克數或毫升數 (例如 2700)
  unitType?: 'g' | 'ml';            // 單位 (預設 'g')
  tagType?: TagType;                // 本週特價 / 黑鑽卡 / 常駐推薦
  historicalBenchmark?: HistoricalBenchmark; // 近期低點 / 常態價格 / 偏高
  storageType?: 'cold' | 'freeze' | 'room';  // 冷藏 / 冷凍 / 常溫
  note?: string;                    // 備註提示
  imageUrl?: string;                // 線上圖片網址
  localImage?: string;              // 本地圖片路徑
  priceSource?: 'warehouse_only' | 'online_catalog'; // 賣場限定(現場標牌/社群) vs 官網線上價
  costcoItemNumber?: string;        // 好市多官方貨號 (如 '110478')
  verifiedSource?: string;          // 驗證情報來源 (例如 '今購百科 2026/09 實拍照')
  historicalRange?: { minPer100g: number; maxPer100g: number }; // 歷史價格區間 (如 $18.1~$21.5)
}

export interface ComputedProduct extends Product {
  currentPrice: number;             // 當前實際總價 (原價 - 折讓)
  pricePer100g: number;             // 當前每 100g 單價 (唯一核心指標)
  originalPricePer100g: number;     // 原價每 100g 單價
  isDiscounted: boolean;            // 是否特價中
  savingsPer100g: number;           // 每 100g 省下金額
  discountPercent: number;          // 折扣百分比 (例如 15 表示打 85 折/省 15%)
  unitType: 'g' | 'ml';
}

export type SortOption = 
  | 'price_asc'        // 100g 單價由低到高 (最推薦)
  | 'price_desc'       // 100g 單價由高到低
  | 'discount_desc'    // 折扣折讓金額最高
  | 'total_price_asc'; // 總金額由低到高

export type SpecialFilter = 
  | 'all' 
  | 'favorites'        // ❤️ 我的珍藏
  | 'warehouse_only'   // 🏬 賣場限定 / Uber Eats
  | 'family_size'      // 🏠 一般家庭規格 (排除超大份量)
  | 'bulk_only'        // 📦 超大量／量販批發 (≥3kg)
  | 'by_weight'        // ⚖️ 賣場秤重品 (公斤牌價)
  | 'weekly_sale' 
  | 'black_card' 
  | 'historical_low' 
  | 'everyday_value';
