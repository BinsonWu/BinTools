import React, { useState, useMemo } from 'react';
import { Calculator, RefreshCw, Plus, Sparkles, Check } from 'lucide-react';
import { calculate100gPrice, calculateKgPriceTo100g } from '../utils/calculator';

interface CustomComparedItem {
  id: string;
  name: string;
  pricePer100g: number;
  totalPrice: number;
  spec: string;
}

interface QuickConverterProps {
  onAddCustomToCompare: (item: CustomComparedItem) => void;
}

export const QuickConverter: React.FC<QuickConverterProps> = ({ onAddCustomToCompare }) => {
  // Mode: 'kg' (看公斤標價牌) | 'bulk' (大包裝總價)
  const [mode, setMode] = useState<'kg' | 'bulk'>('kg');

  // Mode 1: 看公斤牌
  const [kgPriceInput, setKgPriceInput] = useState<string>('215');

  // Mode 2: 大包裝
  const [bulkPriceInput, setBulkPriceInput] = useState<string>('599');
  const [bulkWeightInput, setBulkWeightInput] = useState<string>('1.13');
  const [weightUnit, setWeightUnit] = useState<'g' | 'kg' | 'ml' | '台斤'>('kg');
  const [customItemName, setCustomItemName] = useState<string>('現場自選食物');
  const [hasAdded, setHasAdded] = useState<boolean>(false);

  // 計算 Mode 1 結果
  const mode1Result = useMemo(() => {
    const val = parseFloat(kgPriceInput);
    if (isNaN(val) || val <= 0) return 0;
    return calculateKgPriceTo100g(val);
  }, [kgPriceInput]);

  // 計算 Mode 2 結果
  const mode2Result = useMemo(() => {
    const price = parseFloat(bulkPriceInput);
    const weightRaw = parseFloat(bulkWeightInput);
    if (isNaN(price) || isNaN(weightRaw) || price <= 0 || weightRaw <= 0) return 0;
    
    let totalGrams = weightRaw;
    if (weightUnit === 'kg') {
      totalGrams = weightRaw * 1000;
    } else if (weightUnit === '台斤') {
      totalGrams = weightRaw * 600;
    }
    return calculate100gPrice(price, totalGrams);
  }, [bulkPriceInput, bulkWeightInput, weightUnit]);

  // 當前換算器結果
  const currentResult = mode === 'kg' ? mode1Result : mode2Result;
  const currentTotal = mode === 'kg' 
    ? (parseFloat(kgPriceInput) || 0) 
    : (parseFloat(bulkPriceInput) || 0);

  const handleAddCompare = () => {
    if (currentResult <= 0) return;
    const spec = mode === 'kg' 
      ? `看公斤牌: NT$ ${kgPriceInput}/kg` 
      : `大包裝: NT$ ${bulkPriceInput} / ${bulkWeightInput}${weightUnit}`;
    
    onAddCustomToCompare({
      id: `custom-${Date.now()}`,
      name: customItemName || (mode === 'kg' ? `自選公斤品 ($${kgPriceInput}/kg)` : `自選食物 ($${bulkPriceInput})`),
      pricePer100g: currentResult,
      totalPrice: currentTotal,
      spec
    });
    setHasAdded(true);
    setTimeout(() => setHasAdded(false), 2000);
  };

  return (
    <div id="quick-converter" className="bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950 rounded-2xl border border-slate-800 shadow-2xl p-4 sm:p-6 mb-8 relative overflow-hidden">
      {/* Background Decorative Glow */}
      <div className="absolute -right-16 -top-16 w-64 h-64 bg-rose-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -left-16 -bottom-16 w-64 h-64 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header & Mode Tabs */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5 border-b border-slate-800/80 pb-4">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400">
            <Calculator className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white tracking-tight flex items-center">
              好市多現場 100g 萬用食物換算器
              <span className="ml-2 text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                全食物支援
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              支援肉品、生鮮、零食、堅果、咖啡豆、烘焙、米麵乾貨、飲料全品項換算
            </p>
          </div>
        </div>

        {/* Mode Switcher */}
        <div className="flex items-center p-1 bg-slate-950/80 rounded-xl border border-slate-800 self-start sm:self-auto">
          <button
            onClick={() => setMode('kg')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              mode === 'kg'
                ? 'bg-rose-600 text-white shadow-md shadow-rose-900/40'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            模式一：看公斤牌 (NT$/kg)
          </button>
          <button
            onClick={() => setMode('bulk')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              mode === 'bulk'
                ? 'bg-rose-600 text-white shadow-md shadow-rose-900/40'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            模式二：大包裝總價換算
          </button>
        </div>
      </div>

      {/* Main Interactive Calculation Area */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-center">
        {/* Left: Input Controls */}
        <div className="lg:col-span-7 space-y-4">
          {mode === 'kg' ? (
            /* Mode 1 Inputs */
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5 flex items-center justify-between">
                <span>好市多標價牌上的「每公斤價格（NT$/kg）」：</span>
                <span className="text-[11px] text-slate-400">生鮮肉品/海鮮/水果適用</span>
              </label>
              <div className="relative">
                <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 font-bold text-lg">
                  $
                </span>
                <input
                  type="number"
                  inputMode="decimal"
                  value={kgPriceInput}
                  onChange={(e) => setKgPriceInput(e.target.value)}
                  placeholder="如: 489"
                  className="w-full pl-9 pr-24 py-3.5 bg-slate-950/90 border border-slate-700/80 rounded-xl text-white text-2xl font-mono font-bold focus:outline-none focus:ring-2 focus:ring-rose-500 focus:border-rose-500 transition-all shadow-inner"
                />
                <span className="absolute right-3.5 top-1/2 -translate-y-1/2 text-xs font-semibold text-slate-400 bg-slate-800/80 px-2 py-1 rounded-md border border-slate-700">
                  NT$ / kg
                </span>
              </div>

              {/* Quick Stepper Presets */}
              <div className="flex flex-wrap items-center gap-1.5 mt-2.5">
                <span className="text-xs text-slate-500 mr-1">熱門常買：</span>
                {[
                  { label: '清雞胸肉 215/kg (#110478)', val: '215' },
                  { label: '冷藏雞腿 245/kg (#118583)', val: '245' },
                  { label: '豬梅花肉 270/kg (#111452)', val: '270' },
                  { label: '豬五花肉 315/kg (#112390)', val: '315' },
                  { label: '嫩肩里肌 489/kg (#67404)', val: '489' },
                  { label: '牛肋條 659/kg (#95123)', val: '659' },
                  { label: '挪威鮭魚 699/kg (#89104)', val: '699' },
                  { label: '無骨牛小排 1299/kg (#87754)', val: '1299' },
                ].map((preset) => (
                  <button
                    key={preset.val}
                    onClick={() => setKgPriceInput(preset.val)}
                    className="text-[11px] px-2.5 py-1 rounded-lg bg-slate-800/70 hover:bg-slate-700 text-slate-300 border border-slate-700/60 transition-colors"
                  >
                    {preset.label}
                  </button>
                ))}
                <button
                  onClick={() => setKgPriceInput('')}
                  className="text-[11px] px-2 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 text-rose-400 border border-rose-900/40 ml-auto flex items-center space-x-1"
                >
                  <RefreshCw className="w-3 h-3" />
                  <span>清除</span>
                </button>
              </div>
            </div>
          ) : (
            /* Mode 2 Inputs */
            <div className="space-y-3">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    包裝標籤總金額 (NT$)
                  </label>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 font-bold">
                      $
                    </span>
                    <input
                      type="number"
                      inputMode="decimal"
                      value={bulkPriceInput}
                      onChange={(e) => setBulkPriceInput(e.target.value)}
                      placeholder="如: 599"
                      className="w-full pl-8 pr-3 py-2.5 bg-slate-950/90 border border-slate-700/80 rounded-xl text-white text-xl font-mono font-bold focus:outline-none focus:ring-2 focus:ring-rose-500 focus:border-rose-500 shadow-inner"
                    />
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label className="text-xs font-medium text-slate-300">
                      總重量 / 容積
                    </label>
                    <div className="flex rounded-lg bg-slate-950 border border-slate-800 p-0.5 text-[10px]">
                      {(['g', 'kg', 'ml', '台斤'] as const).map((unit) => (
                        <button
                          key={unit}
                          onClick={() => setWeightUnit(unit)}
                          className={`px-1.5 py-0.5 rounded ${
                            weightUnit === unit
                              ? 'bg-rose-600 text-white font-bold'
                              : 'text-slate-400 hover:text-slate-200'
                          }`}
                        >
                          {unit}
                        </button>
                      ))}
                    </div>
                  </div>
                  <input
                    type="number"
                    inputMode="decimal"
                    value={bulkWeightInput}
                    onChange={(e) => setBulkWeightInput(e.target.value)}
                    placeholder={weightUnit === 'kg' ? '如: 1.13' : weightUnit === '台斤' ? '如: 2' : '如: 1130'}
                    className="w-full px-3 py-2.5 bg-slate-950/90 border border-slate-700/80 rounded-xl text-white text-xl font-mono font-bold focus:outline-none focus:ring-2 focus:ring-rose-500 focus:border-rose-500 shadow-inner"
                  />
                </div>
              </div>

              {/* Optional Custom Item Name */}
              <div className="pt-1">
                <input
                  type="text"
                  value={customItemName}
                  onChange={(e) => setCustomItemName(e.target.value)}
                  placeholder="自訂商品名稱（例如：特大盒裝鮭魚壽司、美式貝果）"
                  className="w-full px-3 py-1.5 bg-slate-950/70 border border-slate-800 rounded-lg text-xs text-slate-300 focus:outline-none focus:ring-1 focus:ring-rose-500"
                />
              </div>

              {/* Costco All-Food Common Package Sizes Quick Buttons */}
              <div className="flex flex-wrap items-center gap-1.5 pt-1">
                <span className="text-xs text-slate-500 mr-1">好市多全食物常見大規格：</span>
                {[
                  { label: '1 台斤 (600g 傳統市場比價)', val: '1', unit: '台斤' as const },
                  { label: '1.13 kg (堅果/咖啡豆)', val: '1.13', unit: 'kg' as const },
                  { label: '1.35 kg (貝果12入)', val: '1350', unit: 'g' as const },
                  { label: '2.7 kg (清雞胸/腿肉)', val: '2.7', unit: 'kg' as const },
                  { label: '3.78 L (鮮乳2入)', val: '3780', unit: 'ml' as const },
                  { label: '9.0 kg (台梗九號米)', val: '9.0', unit: 'kg' as const },
                ].map((spec) => (
                  <button
                    key={spec.label}
                    onClick={() => {
                      setBulkWeightInput(spec.val);
                      setWeightUnit(spec.unit);
                    }}
                    className="text-[11px] px-2.5 py-1 rounded-lg bg-slate-800/70 hover:bg-slate-700 text-slate-300 border border-slate-700/60 transition-colors"
                  >
                    {spec.label}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right: Giant 100g Result Display */}
        <div className="lg:col-span-5 bg-slate-950/90 rounded-xl p-4 sm:p-5 border border-slate-800 flex flex-col justify-between shadow-xl">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span className="flex items-center font-medium">
              <Sparkles className="w-3.5 h-3.5 text-rose-400 mr-1" />
              全品項唯一基準 (換算結果)
            </span>
            <span className="text-[11px] text-slate-500">
              {mode === 'kg' ? '每公斤 ÷ 10' : '總價 ÷ 總重 × 100'}
            </span>
          </div>

          <div className="py-2 flex items-baseline justify-between border-b border-slate-800/80">
            <div className="flex items-baseline space-x-2">
              <span className="text-sm font-bold text-rose-400">NT$</span>
              <span className="text-4xl sm:text-5xl font-extrabold font-mono text-white tracking-tight">
                {currentResult > 0 ? currentResult.toFixed(1) : '0.0'}
              </span>
            </div>
            <span className="text-xs sm:text-sm font-bold px-2.5 py-1 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/20">
              / 100{weightUnit === 'ml' && mode === 'bulk' ? 'ml' : 'g'}
            </span>
          </div>

          {/* Value context & Action */}
          <div className="pt-3 flex items-center justify-between">
            <div className="text-xs text-slate-400">
              {currentResult > 0 ? (
                <span>
                  每台斤 (600g) 約 <b>NT$ {Math.round(currentResult * 6)}</b>
                </span>
              ) : (
                <span className="text-slate-500">請輸入有效金額</span>
              )}
            </div>

            <button
              onClick={handleAddCompare}
              disabled={currentResult <= 0}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                hasAdded
                  ? 'bg-emerald-600 text-white'
                  : currentResult > 0
                  ? 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 active:scale-95'
                  : 'bg-slate-900 text-slate-600 border border-slate-800/60 cursor-not-allowed'
              }`}
            >
              {hasAdded ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-300" />
                  <span>已加入比價</span>
                </>
              ) : (
                <>
                  <Plus className="w-3.5 h-3.5 text-rose-400" />
                  <span>加入比價暫存</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
