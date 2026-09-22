import { Product } from '../types/product';
import productsData from './products.json';

/**
 * 本資料庫由 scripts/import_all_costco_food.py 自動由好市多官方「食品飲料」全分類 API (costco_products.db) 同步產出
 * 包含官方全品項、卜蜂去骨清雞腿、生鮮肉品、水產、食用油、堅果與 100g/100ml 精準單價基準換算
 * 總收錄商品數：1270 項
 */
export const MOCK_PRODUCTS: Product[] = (productsData as unknown) as Product[];
