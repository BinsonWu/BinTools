import React from 'react';
import { X, Scale } from 'lucide-react';
import { ComputedProduct } from '../types/product';

export interface ComparedCustomItem {
  id: string;
  name: string;
  pricePer100g: number;
  totalPrice: number;
  spec: string;
}

interface CompareDrawerProps {
  pinnedProducts: ComputedProduct[];
  customItems: ComparedCustomItem[];
  onRemoveProduct: (id: string) => void;
  onRemoveCustom: (id: string) => void;
  onClearAll: () => void;
}

export const CompareDrawer: React.FC<CompareDrawerProps> = ({
  pinnedProducts,
  customItems,
  onRemoveProduct,
  onRemoveCustom,
  onClearAll
}) => {
  const totalItems = pinnedProducts.length + customItems.length;
  if (totalItems === 0) return null;

  // Combine items into unified compare shape
  const allCompared = [
    ...pinnedProducts.map((p) => ({
      id: p.id,
      name: p.name,
      pricePer100g: p.pricePer100g,
      totalPrice: p.currentPrice,
      spec: p.packageSpec,
      unit: p.unitType,
      isCustom: false
    })),
    ...customItems.map((c) => ({
      id: c.id,
      name: c.name,
      pricePer100g: c.pricePer100g,
      totalPrice: c.totalPrice,
      spec: c.spec,
      unit: 'g' as const,
      isCustom: true
    }))
  ];

  // Find lowest price item
  const minPrice = Math.min(...allCompared.map((item) => item.pricePer100g));

  return (
    <div className="fixed bottom-0 left-0 right-0 z-40 bg-slate-900/95 backdrop-blur-xl border-t border-slate-700/80 shadow-2xl p-4 sm:p-5 transition-all animate-in slide-in-from-bottom-5">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <div className="p-1.5 rounded-lg bg-rose-500/20 text-rose-400 border border-rose-500/30">
              <Scale className="w-4 h-4" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-white flex items-center">
                100g 現場比價對決席 ({totalItems} / 4)
                <span className="ml-2 text-[10px] text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-800/60">
                  基準化 NT$ / 100g
                </span>
              </h4>
            </div>
          </div>

          <button
            onClick={onClearAll}
            className="text-xs text-slate-400 hover:text-rose-400 transition-colors"
          >
            清空所有比價
          </button>
        </div>

        {/* Compared Items Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          {allCompared.map((item) => {
            const isBest = item.pricePer100g === minPrice && allCompared.length > 1;
            const diffFromMin = item.pricePer100g - minPrice;
            const diffPercent = minPrice > 0 ? Math.round((diffFromMin / minPrice) * 100) : 0;

            return (
              <div
                key={item.id}
                className={`relative p-3 rounded-xl bg-slate-950 border transition-all ${
                  isBest
                    ? 'border-emerald-500/60 ring-1 ring-emerald-500/40'
                    : 'border-slate-800'
                }`}
              >
                {/* Remove button */}
                <button
                  onClick={() =>
                    item.isCustom
                      ? onRemoveCustom(item.id)
                      : onRemoveProduct(item.id)
                  }
                  className="absolute top-2 right-2 text-slate-500 hover:text-rose-400 p-1 rounded-md"
                >
                  <X className="w-3.5 h-3.5" />
                </button>

                {/* Best Value Tag */}
                {isBest && (
                  <span className="inline-block text-[10px] font-bold px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 mb-1">
                    👑 CP值冠軍
                  </span>
                )}
                {item.isCustom && (
                  <span className="inline-block text-[10px] font-bold px-1.5 py-0.2 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30 mb-1 ml-1">
                    現場手動輸入
                  </span>
                )}

                <h5 className="text-xs font-bold text-slate-200 line-clamp-1 pr-5">
                  {item.name}
                </h5>
                <p className="text-[10px] text-slate-400 mb-2 truncate">
                  {item.spec}
                </p>

                {/* 100g Price */}
                <div className="flex items-baseline justify-between pt-1 border-t border-slate-900">
                  <div>
                    <span className="text-[10px] text-slate-400">每100{item.unit}: </span>
                    <span className="text-base font-extrabold font-mono text-white">
                      ${item.pricePer100g.toFixed(1)}
                    </span>
                  </div>
                  <span className="text-[10px] text-slate-400 font-mono">
                    總價 ${item.totalPrice}
                  </span>
                </div>

                {/* Relative Difference */}
                {allCompared.length > 1 && (
                  <div className="mt-1.5 text-[10px] font-medium">
                    {isBest ? (
                      <span className="text-emerald-400">目前最省單價首選</span>
                    ) : (
                      <span className="text-rose-400">
                        比最便宜貴 +${diffFromMin.toFixed(1)} (+{diffPercent}%)
                      </span>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
