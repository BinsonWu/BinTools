import { Product, ComputedProduct, HistoricalBenchmark } from '../types/product';

/**
 * 計算每 100g (或 100ml) 單價
 * 若商品為秤重品且有精準每公斤牌價 (pricePerKg)，直接以 (pricePerKg / 10) 算出 100% 真實單價！
 * 避免先估算單包重量再反除所產生的四捨五入誤差。
 */
export function calculate100gPrice(price: number, weightInGrams: number, pricePerKg?: number): number {
  if (pricePerKg && pricePerKg > 0) {
    return Math.round((pricePerKg / 10) * 10) / 10;
  }
  if (!weightInGrams || weightInGrams <= 0) return 0;
  const result = (price / weightInGrams) * 100;
  return Math.round(result * 10) / 10;
}

/**
 * 賣場看公斤牌標價 (NT$/kg) 換算為 每 100g 單價 (直接除以 10)
 */
export function calculateKgPriceTo100g(pricePerKg: number): number {
  if (!pricePerKg || pricePerKg <= 0) return 0;
  return Math.round((pricePerKg / 10) * 10) / 10;
}

/**
 * 將原始 Product 補充所有計算欄位
 */
export function computeProduct(product: Product): ComputedProduct {
  const discount = Math.max(0, product.discountAmount || 0);
  const currentPrice = Math.max(0, product.originalPrice - discount);
  const totalWeight = Math.max(1, product.totalWeightInGrams);
  const unitType = product.unitType || 'g';

  // 若為秤重商品，使用真實公斤牌價除以 10
  let pricePer100g: number;
  let originalPricePer100g: number;

  if (product.pricingType === 'by_weight' && product.pricePerKg && product.pricePerKg > 0) {
    originalPricePer100g = Math.round((product.pricePerKg / 10) * 10) / 10;
    const currentPricePerKg = Math.max(0, product.pricePerKg - (discount > 0 ? (discount / (totalWeight / 1000)) : 0));
    pricePer100g = Math.round((currentPricePerKg / 10) * 10) / 10;
  } else {
    originalPricePer100g = calculate100gPrice(product.originalPrice, totalWeight);
    pricePer100g = calculate100gPrice(currentPrice, totalWeight);
  }

  const savingsPer100g = Math.max(0, Math.round((originalPricePer100g - pricePer100g) * 10) / 10);
  const isDiscounted = discount > 0;
  const discountPercent = isDiscounted 
    ? Math.round((discount / product.originalPrice) * 100) 
    : 0;

  return {
    ...product,
    unitType,
    currentPrice,
    pricePer100g,
    originalPricePer100g,
    isDiscounted,
    savingsPer100g,
    discountPercent
  };
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('zh-TW', {
    style: 'currency',
    currency: 'TWD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount);
}

export function formatWeight(weightInGrams: number, unit: 'g' | 'ml' = 'g'): string {
  if (unit === 'ml') {
    if (weightInGrams >= 1000) {
      return `${(weightInGrams / 1000).toFixed(2).replace(/\.00$/, '')} L`;
    }
    return `${weightInGrams} ml`;
  }
  if (weightInGrams >= 1000) {
    return `${(weightInGrams / 1000).toFixed(2).replace(/\.00$/, '')} kg`;
  }
  return `${weightInGrams} g`;
}

export function getBenchmarkInfo(benchmark?: HistoricalBenchmark): {
  label: string;
  bgClass: string;
  textClass: string;
  dotClass: string;
} {
  switch (benchmark) {
    case 'historical_low':
      return {
        label: '近期低點',
        bgClass: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
        textClass: 'text-emerald-400',
        dotClass: 'bg-emerald-400 animate-pulse'
      };
    case 'above_average':
      return {
        label: '稍高於均價',
        bgClass: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
        textClass: 'text-amber-400',
        dotClass: 'bg-amber-400'
      };
    case 'standard':
    default:
      return {
        label: '常態行情',
        bgClass: 'bg-slate-500/10 border-slate-500/30 text-slate-300',
        textClass: 'text-slate-300',
        dotClass: 'bg-slate-400'
      };
  }
}

/**
 * 判斷是否為超大份量／營業用批發包裝 (如 2.5kg X 2入, 15kg 米, 棧板裝等)
 */
export const isBulkProduct = (p: { name: string; packageSpec?: string; totalWeightInGrams?: number }): boolean => {
  const grams = p.totalWeightInGrams || 0;
  if (grams >= 3000) return true;
  const combined = `${p.name} ${p.packageSpec || ''}`.toLowerCase();
  if (/(\d+(?:\.\d+)?)\s*(?:公斤|kg)\s*[xX*]\s*([2-9]|\d{2,})/i.test(combined)) return true;
  if (/(\d+(?:\.\d+)?)\s*(?:公克|克|g)\s*[xX*]\s*([6-9]|\d{2,})/i.test(combined) && grams >= 2000) return true;
  if (/棧板|整箱|箱裝|營業用|商業量販/.test(combined)) return true;
  return false;
};
