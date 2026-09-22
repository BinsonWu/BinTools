import React from 'react';
import { Calculator, Sparkles, Database, ShieldCheck, Heart } from 'lucide-react';

interface NavbarProps {
  onScrollToConverter: () => void;
  activeSalesCount: number;
  blackCardCount: number;
  totalProductsCount: number;
  favoritesCount?: number;
  onFilterFavorites?: () => void;
  isFilteringFavorites?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  onScrollToConverter,
  activeSalesCount,
  blackCardCount,
  totalProductsCount,
  favoritesCount = 0,
  onFilterFavorites,
  isFilteringFavorites = false
}) => {
  return (
    <header className="sticky top-0 z-30 bg-slate-900/90 backdrop-blur-md border-b border-slate-800 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-rose-600 to-rose-700 shadow-md shadow-rose-900/30 border border-rose-500/30">
              <span className="text-xl">🥩</span>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-xl tracking-tight text-white flex items-center">
                  <span className="text-rose-500 mr-1">COSTCO</span> 100g 比價
                </span>
                <span className="text-[10px] uppercase font-bold tracking-widest px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center space-x-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  <span>SQLite DB</span>
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">
                生鮮肉品海鮮 · 換算 100g 唯一基準 · 本地圖片與特價資料庫
              </p>
            </div>
          </div>

          {/* Quick Metrics & Action */}
          <div className="flex items-center space-x-2 sm:space-x-4">
            <div className="hidden md:flex items-center space-x-3 text-xs">
              <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-slate-800/80 border border-slate-700/60 text-slate-300">
                <Database className="w-3.5 h-3.5 text-emerald-400" />
                <span>已存 <b>{totalProductsCount}</b> 款</span>
              </div>
              <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-rose-950/50 border border-rose-800/60 text-rose-300">
                <Sparkles className="w-3.5 h-3.5 text-rose-400" />
                <span>特價 <b>{activeSalesCount}</b> 檔</span>
              </div>
              <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-amber-950/40 border border-amber-700/50 text-amber-300">
                <ShieldCheck className="w-3.5 h-3.5 text-amber-400" />
                <span>黑鑽 <b>{blackCardCount}</b> 款</span>
              </div>
              <button
                onClick={onFilterFavorites}
                className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-full border transition-all cursor-pointer ${
                  isFilteringFavorites
                    ? 'bg-rose-600 text-white border-rose-500 shadow-md shadow-rose-950/50 scale-105'
                    : favoritesCount > 0
                      ? 'bg-rose-950/50 border-rose-800/70 text-rose-300 hover:bg-rose-900/60'
                      : 'bg-slate-800/80 border-slate-700/60 text-slate-400 hover:text-slate-300'
                }`}
                title="點擊切換查看我的珍藏"
              >
                <Heart className={`w-3.5 h-3.5 ${isFilteringFavorites || favoritesCount > 0 ? 'fill-rose-400 text-rose-400' : 'text-slate-400'} ${isFilteringFavorites ? 'fill-white text-white' : ''}`} />
                <span>珍藏 <b>{favoritesCount}</b> 款</span>
              </button>
            </div>

            <button
              onClick={onScrollToConverter}
              className="flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-gradient-to-r from-rose-600 to-rose-500 hover:from-rose-500 hover:to-rose-400 text-white font-medium text-xs sm:text-sm shadow-md shadow-rose-950/40 transition-all active:scale-95 border border-rose-400/30"
            >
              <Calculator className="w-4 h-4" />
              <span>現場快速換算器</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
