import React, { useState, useMemo } from 'react';
import { Navbar } from './components/Navbar';
import { QuickConverter } from './components/QuickConverter';
import { FilterBar } from './components/FilterBar';
import { ProductGrid } from './components/ProductGrid';
import { CompareDrawer, ComparedCustomItem } from './components/CompareDrawer';
import { MOCK_PRODUCTS } from './data/mockProducts';
import { computeProduct, isBulkProduct } from './utils/calculator';
import { ProductCategory, SpecialFilter, SortOption, ComputedProduct } from './types/product';

export const App: React.FC = () => {
  // State for filters
  const [selectedCategory, setSelectedCategory] = useState<ProductCategory | 'all'>('all');
  const [selectedSpecial, setSelectedSpecial] = useState<SpecialFilter>('all');
  const [excludeBulk, setExcludeBulk] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [sortOption, setSortOption] = useState<SortOption>('price_asc');

  // Compare Drawer State
  const [pinnedProducts, setPinnedProducts] = useState<ComputedProduct[]>([]);
  const [customComparedItems, setCustomComparedItems] = useState<ComparedCustomItem[]>([]);

  // User Favorites State (stored in localStorage)
  const [favoriteIds, setFavoriteIds] = useState<string[]>(() => {
    try {
      const saved = localStorage.getItem('costco_favorite_products');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const handleToggleFavorite = (productId: string) => {
    setFavoriteIds((prev) => {
      const updated = prev.includes(productId)
        ? prev.filter((id) => id !== productId)
        : [...prev, productId];
      try {
        localStorage.setItem('costco_favorite_products', JSON.stringify(updated));
      } catch (e) {
        console.error(e);
      }
      return updated;
    });
  };

  // User In-situ Price Overrides (stored in localStorage)
  const [priceOverrides, setPriceOverrides] = useState<Record<string, { price: number; isKgPrice?: boolean }>>(() => {
    try {
      const saved = localStorage.getItem('costco_price_overrides');
      return saved ? JSON.parse(saved) : {};
    } catch {
      return {};
    }
  });

  const handleUpdatePrice = (productId: string, newPrice: number, isKgPrice?: boolean) => {
    setPriceOverrides((prev) => {
      const updated = { ...prev };
      if (newPrice <= 0) {
        delete updated[productId];
      } else {
        updated[productId] = { price: newPrice, isKgPrice };
      }
      try {
        localStorage.setItem('costco_price_overrides', JSON.stringify(updated));
      } catch (e) {
        console.error(e);
      }
      return updated;
    });
  };

  // Compute products with 100g prices and overrides
  const allComputedProducts = useMemo(() => {
    return MOCK_PRODUCTS.map((p) => {
      const override = priceOverrides[p.id];
      if (override) {
        if (override.isKgPrice) {
          return computeProduct({
            ...p,
            pricingType: 'by_weight',
            pricePerKg: override.price,
            originalPrice: Math.round(override.price * (p.totalWeightInGrams / 1000)),
            verifiedSource: '顧客現場回報修正'
          });
        } else {
          return computeProduct({
            ...p,
            originalPrice: override.price,
            verifiedSource: '顧客現場回報修正'
          });
        }
      }
      return computeProduct(p);
    });
  }, [priceOverrides]);

  // Filter & Sort Logic
  const filteredProducts = useMemo(() => {
    let list = allComputedProducts;

    // 1. Category Filter
    if (selectedCategory !== 'all') {
      list = list.filter((p) => p.category === selectedCategory);
    }

    // 2. Special Deal Filter
    if (selectedSpecial !== 'all') {
      if (selectedSpecial === 'favorites') {
        list = list.filter((p) => favoriteIds.includes(p.id));
      } else if (selectedSpecial === 'warehouse_only') {
        list = list.filter((p) => p.priceSource === 'warehouse_only' || p.subCategory?.includes('賣場限定') || p.note?.includes('賣場限定'));
      } else if (selectedSpecial === 'family_size') {
        list = list.filter((p) => !isBulkProduct(p));
      } else if (selectedSpecial === 'bulk_only') {
        list = list.filter((p) => isBulkProduct(p));
      } else if (selectedSpecial === 'weekly_sale') {
        list = list.filter((p) => p.isDiscounted);
      } else if (selectedSpecial === 'by_weight') {
        list = list.filter((p) => p.pricingType === 'by_weight');
      } else if (selectedSpecial === 'black_card') {
        list = list.filter((p) => p.tagType === 'black_card');
      } else if (selectedSpecial === 'historical_low') {
        list = list.filter((p) => p.historicalBenchmark === 'historical_low');
      } else if (selectedSpecial === 'everyday_value') {
        list = list.filter((p) => p.tagType === 'everyday_value');
      }
    }

    // 2.5 Fast Toggle: Exclude Ultra-Large Bulk Packs
    if (excludeBulk && selectedSpecial !== 'bulk_only') {
      list = list.filter((p) => !isBulkProduct(p));
    }

    // 3. Search Query
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      list = list.filter(
        (p) =>
          p.name.toLowerCase().includes(q) ||
          (p.subCategory && p.subCategory.toLowerCase().includes(q)) ||
          p.packageSpec.toLowerCase().includes(q) ||
          (p.note && p.note.toLowerCase().includes(q)) ||
          (p.costcoItemNumber && p.costcoItemNumber.includes(q))
      );
    }

    // 4. Sorting
    return [...list].sort((a, b) => {
      switch (sortOption) {
        case 'price_asc':
          return a.pricePer100g - b.pricePer100g;
        case 'price_desc':
          return b.pricePer100g - a.pricePer100g;
        case 'discount_desc':
          return (b.discountAmount || 0) - (a.discountAmount || 0);
        case 'total_price_asc':
          return a.currentPrice - b.currentPrice;
        default:
          return 0;
      }
    });
  }, [allComputedProducts, selectedCategory, selectedSpecial, excludeBulk, searchQuery, sortOption, favoriteIds]);

  // Counts for category badges
  const categoryCounts = useMemo(() => {
    const counts: Record<string, number> = { all: allComputedProducts.length };
    allComputedProducts.forEach((p) => {
      counts[p.category] = (counts[p.category] || 0) + 1;
    });
    return counts as Record<ProductCategory | 'all', number>;
  }, [allComputedProducts]);

  // Active metrics
  const activeSalesCount = useMemo(
    () => allComputedProducts.filter((p) => p.isDiscounted).length,
    [allComputedProducts]
  );
  const blackCardCount = useMemo(
    () => allComputedProducts.filter((p) => p.tagType === 'black_card').length,
    [allComputedProducts]
  );

  // Pin / Unpin handlers
  const handleToggleCompare = (product: ComputedProduct) => {
    setPinnedProducts((prev) => {
      const exists = prev.some((item) => item.id === product.id);
      if (exists) {
        return prev.filter((item) => item.id !== product.id);
      }
      if (prev.length + customComparedItems.length >= 4) {
        alert('最多同時比對 4 件商品');
        return prev;
      }
      return [...prev, product];
    });
  };

  const handleAddCustomToCompare = (item: ComparedCustomItem) => {
    if (pinnedProducts.length + customComparedItems.length >= 4) {
      alert('最多同時比對 4 件商品');
      return;
    }
    setCustomComparedItems((prev) => [...prev, item]);
  };

  const handleClearFilters = () => {
    setSelectedCategory('all');
    setSelectedSpecial('all');
    setSearchQuery('');
  };

  const scrollToConverter = () => {
    const el = document.getElementById('quick-converter');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans pb-28">
      {/* Top Navbar */}
      <Navbar
        onScrollToConverter={scrollToConverter}
        activeSalesCount={activeSalesCount}
        blackCardCount={blackCardCount}
        totalProductsCount={allComputedProducts.length}
        favoritesCount={favoriteIds.length}
        isFilteringFavorites={selectedSpecial === 'favorites'}
        onFilterFavorites={() => {
          setSelectedSpecial((prev) => (prev === 'favorites' ? 'all' : 'favorites'));
        }}
      />

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 flex-1 w-full">
        {/* Intro Mission Banner */}
        <div className="mb-6 flex flex-col sm:flex-row sm:items-center justify-between bg-gradient-to-r from-slate-900 via-slate-900 to-rose-950/40 rounded-2xl p-4 sm:p-5 border border-slate-800 shadow-lg gap-4">
          <div>
            <div className="flex items-center space-x-2 text-xs font-bold text-rose-400 mb-1">
              <span className="p-1 rounded bg-rose-500/20 border border-rose-500/30">🎯 真實定價引擎</span>
              <span>秤重商品以「每公斤真實標牌」為唯一基準，拒絕盲目估算</span>
            </div>
            <h1 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight">
              告別大包裝總價障眼法，全食物每 100g/100ml 價格一目了然
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              結合今購百科實拍行情與好市多門市標牌，生鮮秤重肉品、海鮮、蔬果、熟食、烘焙全品項精確換算！
            </p>
          </div>

          <div className="flex items-center space-x-3 text-xs bg-slate-950/60 p-3 rounded-xl border border-slate-800/80 shrink-0">
            <div className="text-center px-2 border-r border-slate-800">
              <div className="text-lg font-mono font-bold text-emerald-400">$4.3</div>
              <div className="text-[10px] text-slate-400">全場最低 100ml (氣泡水)</div>
            </div>
            <div className="text-center px-2">
              <div className="text-lg font-mono font-bold text-rose-400">-$200</div>
              <div className="text-[10px] text-slate-400">本週最大折讓 (蟹腳/牛排)</div>
            </div>
          </div>
        </div>

        {/* Section A: Quick Converter Tool */}
        <QuickConverter onAddCustomToCompare={handleAddCustomToCompare} />

        {/* Section B: Filter & Discount Wall */}
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <h2 className="text-lg font-bold text-white tracking-tight flex items-center">
              <span>好市多商品庫與近期特價牆</span>
              <span className="text-xs font-normal text-slate-400 ml-2">
                (共 {filteredProducts.length} 款全食物品項)
              </span>
            </h2>
          </div>
        </div>

        {/* Filter controls */}
        <FilterBar
          selectedCategory={selectedCategory}
          onSelectCategory={setSelectedCategory}
          selectedSpecial={selectedSpecial}
          onSelectSpecial={setSelectedSpecial}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          sortOption={sortOption}
          onSortChange={setSortOption}
          counts={categoryCounts}
          favoritesCount={favoriteIds.length}
          excludeBulk={excludeBulk}
          onToggleExcludeBulk={setExcludeBulk}
        />

        {/* Products Grid */}
        <ProductGrid
          products={filteredProducts}
          pinnedIds={pinnedProducts.map((p) => p.id)}
          onToggleCompare={handleToggleCompare}
          favoriteIds={favoriteIds}
          onToggleFavorite={handleToggleFavorite}
          isFavoritesFilter={selectedSpecial === 'favorites'}
          onClearFilters={handleClearFilters}
          onUpdatePrice={handleUpdatePrice}
        />
      </main>

      {/* Floating Compare Drawer */}
      <CompareDrawer
        pinnedProducts={pinnedProducts}
        customItems={customComparedItems}
        onRemoveProduct={(id) => setPinnedProducts((prev) => prev.filter((p) => p.id !== id))}
        onRemoveCustom={(id) => setCustomComparedItems((prev) => prev.filter((c) => c.id !== id))}
        onClearAll={() => {
          setPinnedProducts([]);
          setCustomComparedItems([]);
        }}
      />
    </div>
  );
};

export default App;
