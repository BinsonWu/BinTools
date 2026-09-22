import React, { useState, useEffect } from 'react';
import { ComputedProduct } from '../types/product';
import { ProductCard } from './ProductCard';
import { PackageOpen, ChevronDown, Layers, Heart } from 'lucide-react';

interface ProductGridProps {
  products: ComputedProduct[];
  pinnedIds: string[];
  onToggleCompare: (product: ComputedProduct) => void;
  favoriteIds?: string[];
  onToggleFavorite?: (productId: string) => void;
  isFavoritesFilter?: boolean;
  onClearFilters: () => void;
  onUpdatePrice?: (productId: string, newPrice: number, isKgPrice?: boolean) => void;
}

const BATCH_SIZE = 40;

export const ProductGrid: React.FC<ProductGridProps> = ({
  products,
  pinnedIds,
  onToggleCompare,
  favoriteIds = [],
  onToggleFavorite,
  isFavoritesFilter = false,
  onClearFilters,
  onUpdatePrice
}) => {
  const [displayCount, setDisplayCount] = useState<number>(BATCH_SIZE);

  // Reset display count when products list changes (e.g. search or category filter changed)
  useEffect(() => {
    setDisplayCount(BATCH_SIZE);
  }, [products]);

  if (products.length === 0) {
    if (isFavoritesFilter) {
      return (
        <div className="bg-slate-900/60 rounded-2xl border border-rose-900/40 p-12 text-center my-8 shadow-xl shadow-rose-950/20">
          <div className="w-14 h-14 rounded-2xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center mx-auto mb-3.5 text-rose-400 shadow-inner">
            <Heart className="w-7 h-7" />
          </div>
          <h3 className="text-lg font-bold text-white mb-1.5 tracking-tight">
            您尚未加入任何「珍藏商品」
          </h3>
          <p className="text-xs text-slate-400 mb-5 max-w-md mx-auto leading-relaxed">
            在任何好市多商品卡片右上角點擊「❤️ 愛心」，就能把常買的生鮮牛排、清雞腿、海鮮或必買好物存入專屬清單，隨時一鍵追蹤 100g 最優單價與即時特價！
          </p>
          <button
            onClick={onClearFilters}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-rose-600 to-rose-500 hover:from-rose-500 hover:to-rose-400 text-white text-xs font-semibold shadow-lg shadow-rose-950/50 transition-all active:scale-95"
          >
            瀏覽好市多全部商品
          </button>
        </div>
      );
    }

    return (
      <div className="bg-slate-900/50 rounded-2xl border border-slate-800 p-12 text-center my-8">
        <PackageOpen className="w-12 h-12 text-slate-600 mx-auto mb-3" />
        <h3 className="text-base font-bold text-slate-200 mb-1">
          查無符合條件之好市多食物
        </h3>
        <p className="text-xs text-slate-400 mb-4 max-w-sm mx-auto">
          請嘗試調整搜尋關鍵字、更換食物分類或清除特價篩選條件。
        </p>
        <button
          onClick={onClearFilters}
          className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-rose-400 border border-slate-700 text-xs font-semibold transition-all"
        >
          重設所有篩選
        </button>
      </div>
    );
  }

  const visibleProducts = products.slice(0, displayCount);
  const hasMore = displayCount < products.length;
  const remainingCount = products.length - displayCount;

  return (
    <div className="space-y-6">
      {/* Product count header */}
      <div className="flex items-center justify-between text-xs text-slate-400 px-1">
        <span>
          共找到 <strong className="text-rose-400 font-semibold">{products.length}</strong> 項好市多食物
          {products.length > BATCH_SIZE && (
            <span className="text-slate-500 ml-1.5">
              (目前已呈現 {visibleProducts.length} 項)
            </span>
          )}
        </span>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6">
        {visibleProducts.map((product) => (
          <ProductCard
            key={product.id}
            product={product}
            isPinnedForCompare={pinnedIds.includes(product.id)}
            onToggleCompare={onToggleCompare}
            isFavorited={favoriteIds.includes(product.id)}
            onToggleFavorite={onToggleFavorite}
            onUpdatePrice={onUpdatePrice}
          />
        ))}
      </div>

      {/* Load More Button */}
      {hasMore && (
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-4 pb-8">
          <button
            onClick={() => setDisplayCount((prev) => prev + BATCH_SIZE)}
            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-medium text-sm shadow-lg shadow-rose-950/40 transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            <ChevronDown className="w-4 h-4" />
            載入更多商品 (還有 {remainingCount > BATCH_SIZE ? `${BATCH_SIZE}+` : remainingCount} 項)
          </button>
          <button
            onClick={() => setDisplayCount(products.length)}
            className="flex items-center gap-1.5 px-4 py-3 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-300 font-medium text-xs border border-slate-700 transition-all"
          >
            <Layers className="w-3.5 h-3.5 text-slate-400" />
            全部展開 ({products.length} 項)
          </button>
        </div>
      )}
    </div>
  );
};

