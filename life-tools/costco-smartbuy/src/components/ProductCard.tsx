import React, { useState } from 'react';
import { Sparkles, Calendar, Plus, Check, ImageOff, Edit3, CheckCircle2, Scale, Heart, Boxes } from 'lucide-react';
import { ComputedProduct } from '../types/product';
import { formatCurrency, getBenchmarkInfo, isBulkProduct } from '../utils/calculator';

interface ProductCardProps {
  product: ComputedProduct;
  isPinnedForCompare: boolean;
  onToggleCompare: (product: ComputedProduct) => void;
  isFavorited?: boolean;
  onToggleFavorite?: (productId: string) => void;
  onUpdatePrice?: (productId: string, newPrice: number, isKgPrice?: boolean) => void;
}

export const ProductCard: React.FC<ProductCardProps> = ({
  product,
  isPinnedForCompare,
  onToggleCompare,
  isFavorited = false,
  onToggleFavorite,
  onUpdatePrice
}) => {
  const benchmark = getBenchmarkInfo(product.historicalBenchmark);
  const isBulk = isBulkProduct(product);
  const [imgError, setImgError] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editPriceInput, setEditPriceInput] = useState(
    product.pricingType === 'by_weight' && product.pricePerKg
      ? product.pricePerKg.toString()
      : product.currentPrice.toString()
  );

  // Storage badge info
  const storageMap: Record<string, { label: string; icon: string; bg: string }> = {
    cold: { label: '冷藏生鮮', icon: '❄️', bg: 'bg-cyan-950/80 border-cyan-800/80 text-cyan-300' },
    freeze: { label: '冷凍食材', icon: '🧊', bg: 'bg-blue-950/80 border-blue-800/80 text-blue-300' },
    frozen: { label: '冷凍食材', icon: '🧊', bg: 'bg-blue-950/80 border-blue-800/80 text-blue-300' },
    room: { label: '常溫/熟食', icon: '🍗', bg: 'bg-amber-950/80 border-amber-800/80 text-amber-300' }
  };
  const storageInfo = storageMap[product.storageType || 'cold'] || storageMap.cold;

  const imageSrc = product.localImage || product.imageUrl || '';

  const handleSavePrice = () => {
    const val = parseFloat(editPriceInput);
    if (!isNaN(val) && val > 0 && onUpdatePrice) {
      onUpdatePrice(product.id, val, product.pricingType === 'by_weight');
    }
    setIsEditing(false);
  };

  const handleResetPrice = () => {
    if (onUpdatePrice) {
      onUpdatePrice(product.id, 0);
    }
    setIsEditing(false);
  };

  return (
    <div
      className={`group relative rounded-2xl bg-gradient-to-b from-slate-900/95 to-slate-950 border transition-all duration-300 hover:shadow-2xl hover:border-slate-700 flex flex-col justify-between overflow-hidden ${
        product.isDiscounted
          ? 'border-rose-900/50 hover:border-rose-700/80 shadow-rose-950/20'
          : 'border-slate-800/80'
      }`}
    >
      {/* Top Banner for Active Discounts */}
      {product.isDiscounted && (
        <div className="bg-gradient-to-r from-rose-600 to-rose-700 text-white px-3.5 py-1.5 text-xs font-bold flex items-center justify-between shadow-md z-10 relative">
          <div className="flex items-center space-x-1.5">
            <span className="inline-block animate-bounce">🔥</span>
            <span>現折 NT$ {product.discountAmount}</span>
            <span className="text-[10px] font-normal opacity-90">
              (約省 {product.discountPercent}%)
            </span>
          </div>
          {product.discountEndDate && (
            <div className="flex items-center space-x-1 text-[11px] font-medium text-rose-100">
              <Calendar className="w-3 h-3" />
              <span>特價至 {product.discountEndDate.slice(5)}</span>
            </div>
          )}
        </div>
      )}

      {/* Product Image Preview Header */}
      <div className="relative w-full h-44 bg-slate-950 overflow-hidden border-b border-slate-800/80">
        {imageSrc && !imgError ? (
          <img
            src={imageSrc}
            alt={product.name}
            onError={() => setImgError(true)}
            loading="lazy"
            className="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-500 ease-out brightness-95 group-hover:brightness-105"
          />
        ) : (
          <div className="w-full h-full flex flex-col items-center justify-center text-slate-600 bg-slate-900/60">
            <ImageOff className="w-8 h-8 mb-1 text-slate-700" />
            <span className="text-xs text-slate-500">好市多食物商品</span>
          </div>
        )}

        {/* Gradient Shadow Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent opacity-80" />

        {/* Floating Badges on top of Image */}
        <div className="absolute top-2.5 left-2.5 flex flex-wrap gap-1.5">
          {/* Storage badge */}
          <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-md backdrop-blur-md border shadow-sm flex items-center space-x-1 ${storageInfo.bg}`}>
            <span>{storageInfo.icon}</span>
            <span>{storageInfo.label}</span>
          </span>

          {/* Benchmark */}
          <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-md backdrop-blur-md border shadow-sm flex items-center space-x-1 ${benchmark.bgClass}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${benchmark.dotClass}`} />
            <span>{benchmark.label}</span>
          </span>
        </div>

        {/* Action Buttons on Top-Right */}
        <div className="absolute top-2.5 right-2.5 flex items-center space-x-1.5 z-10">
          {/* Favorite Button */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggleFavorite?.(product.id);
            }}
            className={`p-1.5 rounded-lg text-xs transition-all backdrop-blur-md border shadow-md active:scale-90 ${
              isFavorited
                ? 'bg-rose-600 text-white border-rose-400 shadow-rose-950/60 ring-2 ring-rose-500/50'
                : 'bg-slate-900/80 hover:bg-slate-800 text-slate-300 hover:text-rose-400 border-slate-700/80'
            }`}
            title={isFavorited ? '取消珍藏' : '加入我的珍藏'}
          >
            <Heart className={`w-3.5 h-3.5 transition-transform ${isFavorited ? 'fill-white text-white scale-110' : ''}`} />
          </button>

          {/* Compare Pin Button */}
          <button
            onClick={() => onToggleCompare(product)}
            className={`p-1.5 rounded-lg text-xs transition-all backdrop-blur-md border shadow-md active:scale-90 ${
              isPinnedForCompare
                ? 'bg-rose-600 text-white border-rose-500 shadow-rose-900/60'
                : 'bg-slate-900/80 hover:bg-slate-800 text-slate-300 hover:text-white border-slate-700/80'
            }`}
            title={isPinnedForCompare ? '取消比價' : '加入比價對決席'}
          >
            {isPinnedForCompare ? (
              <Check className="w-3.5 h-3.5" />
            ) : (
              <Plus className="w-3.5 h-3.5" />
            )}
          </button>
        </div>

        {/* Item Number or Pricing Model Pill */}
        <div className="absolute bottom-2 left-2.5 flex items-center space-x-1.5 flex-wrap gap-1">
          {product.costcoItemNumber && (
            <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-md bg-slate-900/90 text-slate-200 border border-slate-700 backdrop-blur-md">
              #{product.costcoItemNumber}
            </span>
          )}
          {product.pricingType === 'by_weight' && (
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-emerald-950/80 text-emerald-300 border border-emerald-700/80 flex items-center space-x-1">
              <Scale className="w-3 h-3" />
              <span>實體公斤牌價</span>
            </span>
          )}
          {product.priceSource === 'warehouse_only' && (
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-amber-950/80 text-amber-300 border border-amber-700/80 flex items-center space-x-1">
              <span>🏪 賣場限定</span>
            </span>
          )}
          {isBulk && (
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-indigo-950/90 text-indigo-300 border border-indigo-700/80 flex items-center space-x-1 shadow-sm backdrop-blur-md">
              <Boxes className="w-3 h-3 text-indigo-400" />
              <span>超大份量{product.totalWeightInGrams >= 1000 ? ` ${(product.totalWeightInGrams / 1000).toFixed(1)}kg` : ''}</span>
            </span>
          )}
        </div>
      </div>

      {/* Card Content & Pricing Details */}
      <div className="p-4 sm:p-5 flex-1 flex flex-col justify-between">
        <div>
          {/* Subcategory & Verified badge */}
          <div className="mb-1 flex items-center justify-between text-[11px]">
            <span className="font-semibold text-rose-400">{product.subCategory || '好市多精選'}</span>
            {product.verifiedSource && (
              <span className="text-[10px] text-slate-400 flex items-center font-sans">
                <CheckCircle2 className="w-3 h-3 text-emerald-400 mr-1" />
                {product.verifiedSource}
              </span>
            )}
          </div>

          {/* Product Name */}
          <h3 className="text-base font-bold text-white tracking-tight leading-snug mb-1 group-hover:text-rose-300 transition-colors line-clamp-1">
            {product.name}
          </h3>

          {/* Spec description */}
          <div className="flex items-center justify-between text-xs text-slate-400 mb-3">
            <span className="line-clamp-1">
              規格：<span className="text-slate-300 font-medium">{product.packageSpec}</span>
            </span>
            {isBulk && (
              <span className="text-[10px] font-medium text-indigo-300 bg-indigo-950/60 border border-indigo-800/80 px-1.5 py-0.5 rounded shrink-0 ml-2">
                商業/大量包
              </span>
            )}
          </div>
        </div>

        {/* Focal Metric: Giant NT$ / 100g Price Box */}
        <div className="bg-slate-950/90 rounded-xl p-3.5 border border-slate-800/90 mb-3 shadow-inner relative">
          <div className="text-[11px] text-slate-400 mb-1 flex items-center justify-between font-medium">
            <span className="text-slate-400">換算每 100{product.unitType} 單價：</span>
            {product.isDiscounted && (
              <span className="text-rose-400 font-semibold text-[10px]">
                原價 ${product.originalPricePer100g.toFixed(1)} / 100{product.unitType}
              </span>
            )}
          </div>

          {product.pricePer100g > 0 ? (
            <div className="flex items-baseline justify-between">
              <div className="flex items-baseline space-x-1.5">
                <span className="text-sm font-bold text-rose-400">NT$</span>
                {/* Massive 100g price typography */}
                <span className="text-3xl sm:text-4xl font-extrabold font-mono text-white tracking-tight">
                  {product.pricePer100g.toFixed(1)}
                </span>
              </div>
              <span className="text-xs font-bold px-2 py-0.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/20">
                / 100{product.unitType}
              </span>
            </div>
          ) : (
            <div className="flex items-center justify-between py-1">
              <span className="text-xs font-bold text-amber-400 bg-amber-500/10 px-2.5 py-1 rounded-lg border border-amber-500/30">
                賣場限定 (線上未標價)
              </span>
              <button
                onClick={() => setIsEditing(true)}
                className="text-xs text-rose-400 hover:text-rose-300 font-semibold underline underline-offset-2 flex items-center gap-1"
              >
                <Edit3 className="w-3 h-3" />
                回報現場價
              </button>
            </div>
          )}

          {/* Historical Range if available */}
          {product.historicalRange && (
            <div className="text-[10px] text-slate-400 mt-1 flex items-center justify-between">
              <span>歷史價格區間：</span>
              <span className="font-mono text-slate-300">
                ${product.historicalRange.minPer100g} ~ ${product.historicalRange.maxPer100g} / 100g
              </span>
            </div>
          )}

          {/* Savings per 100g badge */}
          {product.isDiscounted && product.savingsPer100g > 0 && (
            <div className="mt-1.5 pt-1.5 border-t border-slate-800/80 flex items-center justify-between text-[11px]">
              <span className="text-rose-400 font-bold flex items-center space-x-1">
                <Sparkles className="w-3 h-3 animate-spin" />
                <span>每 100{product.unitType} 現省 NT$ {product.savingsPer100g.toFixed(1)}</span>
              </span>
              <span className="text-slate-500">
                約 {(product.pricePer100g * 6).toFixed(0)} / 台斤
              </span>
            </div>
          )}
        </div>

        {/* Pricing Model & Real-world Store Value */}
        <div className="space-y-1.5 text-xs text-slate-400">
          <div className="flex items-center justify-between">
            <span>
              {product.pricingType === 'by_weight' ? '賣場現場每公斤牌價：' : '賣場標籤總價：'}
            </span>
            <span className="font-bold text-slate-200">
              {product.pricingType === 'by_weight' && product.pricePerKg ? (
                <span className="text-emerald-400 font-mono text-sm">
                  NT$ {product.pricePerKg} / kg
                </span>
              ) : product.currentPrice > 0 ? (
                formatCurrency(product.currentPrice)
              ) : (
                <span className="text-amber-400 text-xs font-normal">待現場回報</span>
              )}
            </span>
          </div>

          {/* Original price basis & origin */}
          <div className="flex items-center justify-between text-[10px] pt-0.5">
            <span className="text-slate-400">原價來源：</span>
            {product.priceOrigin === 'flyer_official' ? (
              <span className="text-emerald-300 bg-emerald-950/70 px-1.5 py-0.5 rounded border border-emerald-800/70 font-medium flex items-center space-x-1" title="已自動自好市多最新特惠專頁同步官方正式原價與折讓">
                <span>🏷️</span>
                <span>官方優惠頁正式原價</span>
              </span>
            ) : product.isEstimatedPrice || product.pricingType === 'by_weight' ? (
              <span className="text-cyan-300 bg-cyan-950/70 px-1.5 py-0.5 rounded border border-cyan-800/70 font-medium flex items-center space-x-1" title="賣場生鮮為公斤牌價，此總金額為依平均單包重量計算之預估值">
                <span>📐</span>
                <span>依包重計算預估</span>
              </span>
            ) : (
              <span className="text-slate-300 bg-slate-900/80 px-1.5 py-0.5 rounded border border-slate-700 font-medium">
                🏬 賣場實體常態定價
              </span>
            )}
          </div>

          {/* Price source and inline edit trigger */}
          <div className="flex items-center justify-between text-[10px] pt-1">
            <span className="text-slate-400">定價機制：</span>
            <div className="flex items-center space-x-1.5">
              {product.priceSource === 'warehouse_only' ? (
                <span className="text-amber-400 font-medium">
                  {product.pricingType === 'by_weight' ? '🏬 賣場秤重牌價' : '🏬 賣場實體定價'}
                </span>
              ) : (
                <span className="text-emerald-400 font-medium">
                  🌐 官網線上標價
                </span>
              )}

              {/* Edit live price button */}
              <button
                onClick={() => setIsEditing(!isEditing)}
                className="text-slate-400 hover:text-rose-400 transition-colors p-0.5 rounded"
                title="現場看到不同價格？點此修正"
              >
                <Edit3 className="w-3 h-3" />
              </button>
            </div>
          </div>

          {/* Inline Edit Form */}
          {isEditing && (
            <div className="mt-2 p-2 bg-slate-950 rounded-lg border border-rose-900/60 text-xs animate-in fade-in">
              <div className="flex items-center justify-between mb-1 text-[11px] text-rose-300">
                <span>現場回報修正：</span>
                <span className="text-[10px] text-slate-400">
                  {product.pricingType === 'by_weight' ? '輸入每公斤 NT$' : '輸入包裝總金額 NT$'}
                </span>
              </div>
              <div className="flex items-center space-x-1.5">
                <input
                  type="number"
                  value={editPriceInput}
                  onChange={(e) => setEditPriceInput(e.target.value)}
                  placeholder={product.pricingType === 'by_weight' ? '如: 215' : '如: 580'}
                  className="w-full px-2 py-1 bg-slate-900 border border-slate-700 rounded text-white font-mono text-xs focus:outline-none focus:ring-1 focus:ring-rose-500"
                />
                <button
                  onClick={handleSavePrice}
                  className="px-2.5 py-1 bg-rose-600 hover:bg-rose-500 text-white rounded font-medium text-xs whitespace-nowrap"
                >
                  儲存
                </button>
                {product.verifiedSource === '顧客現場回報修正' && (
                  <button
                    onClick={handleResetPrice}
                    className="px-2 py-1 bg-amber-950/80 hover:bg-amber-900 text-amber-300 border border-amber-700/60 rounded text-xs whitespace-nowrap"
                    title="清除自訂回報，恢復官方牌價"
                  >
                    重設
                  </button>
                )}
                <button
                  onClick={() => setIsEditing(false)}
                  className="px-2 py-1 bg-slate-800 text-slate-400 hover:text-white rounded text-xs"
                >
                  取消
                </button>
              </div>
            </div>
          )}

          {product.note && (
            <p className="text-[11px] text-slate-400 bg-slate-800/40 p-2 rounded-lg border border-slate-800/60 leading-relaxed line-clamp-2">
              💡 {product.note}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};
