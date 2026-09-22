import React from 'react';
import { Search, ArrowUpDown, Tag, Flame, Award, CheckCircle, Sparkles, Scale, Heart, Store, Boxes, Home, Package } from 'lucide-react';
import { ProductCategory, SpecialFilter, SortOption } from '../types/product';

interface FilterBarProps {
  selectedCategory: ProductCategory | 'all';
  onSelectCategory: (cat: ProductCategory | 'all') => void;
  selectedSpecial: SpecialFilter;
  onSelectSpecial: (spec: SpecialFilter) => void;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  sortOption: SortOption;
  onSortChange: (opt: SortOption) => void;
  counts: Record<ProductCategory | 'all', number>;
  favoritesCount?: number;
  excludeBulk?: boolean;
  onToggleExcludeBulk?: (val: boolean) => void;
}

const CATEGORIES: { id: ProductCategory | 'all'; label: string; icon: string }[] = [
  { id: 'all', label: '全部食物', icon: '🛒' },
  { id: 'beef', label: '牛肉', icon: '🥩' },
  { id: 'chicken', label: '雞肉', icon: '🍗' },
  { id: 'pork', label: '豬肉/羊肉', icon: '🥓' },
  { id: 'seafood', label: '海鮮水產', icon: '🐟' },
  { id: 'produce', label: '生鮮蔬果', icon: '🥦' },
  { id: 'dairy', label: '乳品與蛋', icon: '🥛' },
  { id: 'bakery', label: '烘焙甜點', icon: '🥐' },
  { id: 'deli', label: '熟食即食', icon: '🍕' },
  { id: 'snacks', label: '零食堅果', icon: '🥜' },
  { id: 'pantry', label: '米麵調味', icon: '🌾' },
  { id: 'beverages', label: '飲料咖啡', icon: '☕' },
  { id: 'frozen', label: '冷凍食品', icon: '🧊' },
];

export const FilterBar: React.FC<FilterBarProps> = ({
  selectedCategory,
  onSelectCategory,
  selectedSpecial,
  onSelectSpecial,
  searchQuery,
  onSearchChange,
  sortOption,
  onSortChange,
  counts,
  favoritesCount = 0,
  excludeBulk = false,
  onToggleExcludeBulk
}) => {
  return (
    <div className="space-y-4 mb-6">
      {/* Top row: Search & Sort */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        {/* Search input */}
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="搜尋任何好市多食物（如：貝果、堅果、鮮乳、牛排、咖啡豆、米、洋芋片）..."
            className="w-full pl-10 pr-4 py-2.5 bg-slate-900/90 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-rose-500 focus:border-rose-500 transition-all shadow-inner"
          />
          {searchQuery && (
            <button
              onClick={() => onSearchChange('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-400 hover:text-white px-1 py-0.5"
            >
              清除
            </button>
          )}
        </div>

        {/* Sort Select */}
        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-400 flex items-center whitespace-nowrap">
            <ArrowUpDown className="w-3.5 h-3.5 mr-1 text-slate-400" />
            排序依據：
          </span>
          <select
            value={sortOption}
            onChange={(e) => onSortChange(e.target.value as SortOption)}
            className="bg-slate-900 border border-slate-800 text-slate-200 text-xs font-medium rounded-xl px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-rose-500 cursor-pointer shadow-sm"
          >
            <option value="price_asc">🔥 每 100g 單價 (低到高) [推薦]</option>
            <option value="price_desc">每 100g 單價 (高到低)</option>
            <option value="discount_desc">特價折讓金額最高</option>
            <option value="total_price_asc">總金額 (由低到高)</option>
          </select>
        </div>
      </div>

      {/* Category Pills Slider */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-slate-800">
        {CATEGORIES.map((cat) => {
          const isSelected = selectedCategory === cat.id;
          const count = counts[cat.id] || 0;
          return (
            <button
              key={cat.id}
              onClick={() => onSelectCategory(cat.id)}
              className={`flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all border shrink-0 ${
                isSelected
                  ? 'bg-rose-600 text-white border-rose-500 shadow-md shadow-rose-950/40 scale-[1.02]'
                  : 'bg-slate-900/80 hover:bg-slate-800 text-slate-300 border-slate-800 hover:border-slate-700'
              }`}
            >
              <span>{cat.icon}</span>
              <span>{cat.label}</span>
              <span className={`text-[10px] px-1.5 py-0.2 rounded-full ml-1 font-mono ${
                isSelected ? 'bg-rose-700 text-white' : 'bg-slate-800 text-slate-400'
              }`}>
                {count}
              </span>
            </button>
          );
        })}
      </div>

      {/* Special Offer Pills */}
      <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-slate-800/60 text-xs">
        <span className="text-slate-400 font-medium mr-1 flex items-center">
          <Tag className="w-3.5 h-3.5 mr-1 text-slate-500" />
          特價快篩：
        </span>
        {[
          { id: 'all', label: '全部顯示', icon: null },
          { id: 'favorites', label: `❤️ 我的珍藏 (${favoritesCount})`, icon: Heart },
          { id: 'family_size', label: '🏠 一般家庭量 (<3kg)', icon: Home },
          { id: 'bulk_only', label: '📦 超大量/商業包 (≥3kg)', icon: Package },
          { id: 'warehouse_only', label: '賣場限定 / Uber Eats 🏬', icon: Store },
          { id: 'by_weight', label: '賣場秤重品 (公斤牌價) ⚖️', icon: Scale },
          { id: 'weekly_sale', label: '本週即時特價 🔥', icon: Flame },
          { id: 'black_card', label: '黑鑽卡專屬 💎', icon: Award },
          { id: 'historical_low', label: '近期低點 🟢', icon: CheckCircle },
          { id: 'everyday_value', label: '常駐超值 ⭐', icon: Sparkles },
        ].map((item) => {
          const isSelected = selectedSpecial === item.id;
          const isFavorites = item.id === 'favorites';
          return (
            <button
              key={item.id}
              onClick={() => onSelectSpecial(item.id as SpecialFilter)}
              className={`px-3 py-1 rounded-lg font-medium transition-all border flex items-center space-x-1.5 ${
                isSelected
                  ? isFavorites
                    ? 'bg-rose-600 text-white border-rose-500 shadow-md shadow-rose-950/40 ring-1 ring-rose-400/50'
                    : 'bg-amber-500/20 text-amber-300 border-amber-500/50 shadow-sm'
                  : isFavorites && favoritesCount > 0
                    ? 'bg-rose-950/40 text-rose-300 border-rose-800/80 hover:bg-rose-900/60 shadow-sm'
                    : 'bg-slate-900/60 text-slate-400 border-slate-800/80 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              {item.icon && (
                <item.icon
                  className={`w-3.5 h-3.5 ${
                    isFavorites
                      ? isSelected
                        ? 'fill-white text-white'
                        : favoritesCount > 0
                          ? 'fill-rose-400 text-rose-400'
                          : 'text-slate-400'
                      : ''
                  }`}
                />
              )}
              <span>{item.label}</span>
            </button>
          );
        })}

        {/* Dedicated Fast Toggle: Exclude Ultra-Large Bulk Packs */}
        {onToggleExcludeBulk && (
          <button
            onClick={() => onToggleExcludeBulk(!excludeBulk)}
            className={`px-3 py-1 rounded-lg font-medium transition-all border flex items-center space-x-1.5 ml-auto ${
              excludeBulk
                ? 'bg-rose-500/20 text-rose-300 border-rose-500/60 ring-1 ring-rose-500/40 shadow-sm'
                : 'bg-slate-900/60 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border-slate-800'
            }`}
            title="排除 3kg 以上或多入大箱裝商品 (例如 2.5kg X 2入 等超大量包裝)"
          >
            <Boxes className="w-3.5 h-3.5" />
            <span>{excludeBulk ? '🚫 已過濾排除超大量 (≥3kg)' : '📦 過濾排除超大量 (≥3kg)'}</span>
          </button>
        )}
      </div>
    </div>
  );
};
