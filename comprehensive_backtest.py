from market_data import MarketDataFetcher
from pattern_detector import PatternDetector
from backtest_engine import BacktestEngine
import pandas as pd
import os
from datetime import datetime

def _get_atr_value(candle: pd.Series) -> float:
    for col in ("atr", "ATR", "atr_14", "atr14"):
        if col in candle.index and pd.notna(candle[col]):
            return float(candle[col])
    return 0.0

def _safe_float(v, default=0.0) -> float:
    try:
        if pd.isna(v):
            return float(default)
        return float(v)
    except Exception:
        return float(default)

print("=" * 80)
print("COMPREHENSIVE PATTERN BACKTEST - ALL 11 PATTERNS")
print("=" * 80)

# ==================== FETCH DATA ====================
print("\n📊 Fetching historical data...")
fetcher = MarketDataFetcher()
fetcher.connect()
df = fetcher.get_candles(timeframe_minutes=15, num_candles=2000)
fetcher.disconnect()

print(f"✓ Loaded {len(df)} candles")
print(f"  Period: {df.iloc[0]['time']} to {df.iloc[-1]['time']}")

# ==================== DETECT ALL PATTERNS ====================
print("\n🔍 Detecting ALL patterns...")
detector = PatternDetector(df)

# Use the indicator-enriched dataframe from the detector (contains e.g. ATR)
df = detector.df

# Run comprehensive detection
all_patterns = detector.detect_all_patterns()

print(f"\n✅ Total patterns found: {len(all_patterns)}")

# Filter for quality
quality_patterns = detector.get_high_quality_signals(all_patterns)

# ==================== PATTERN BREAKDOWN ====================
print("\n📋 Pattern Breakdown:")
print("-" * 80)

pattern_counts = {}
for pattern in all_patterns:
    pattern_name = pattern.get('pattern', 'unknown')
    pattern_counts[pattern_name] = pattern_counts.get(pattern_name, 0) + 1

for pattern_name, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {pattern_name:30s}: {count:3d} signals")

# ==================== BACKTEST EACH PATTERN TYPE ====================
print("\n" + "=" * 80)
print("BACKTESTING EACH PATTERN TYPE")
print("=" * 80)

pattern_results = {}

# De-duplication / realism controls
COOLDOWN_BARS = 10

# Signal-quality filters (aim: higher precision / win-rate)
USE_TREND_FILTER = True
USE_RSI_FILTER = True
USE_ATR_FILTER = True
USE_SESSION_FILTER = False

# High-precision mode (target: >=60% win-rate)
HIGH_PRECISION_MODE = True
PATTERN_ALLOWLIST = {
    'falling_wedge',
    'ascending_triangle',
    'bullish_engulfing',
    'double_bottom',
    'rising_wedge',
}
MIN_TRADES_FOR_APPROVAL = 20
MIN_WIN_RATE_FOR_APPROVAL = 60.0
MIN_PROFIT_FACTOR_FOR_APPROVAL = 1.30

RSI_LONG_MAX = 65
RSI_SHORT_MIN = 35

ATR_PERCENTILE_MAX = 0.80

SESSION_START_HOUR = 7
SESSION_END_HOUR = 20

EXPORT_ML_DATASET = True
ML_DATASET_FILENAME = 'logs/ml_dataset.csv'

# Get unique pattern types
unique_patterns = list(set([p.get('pattern', 'unknown') for p in quality_patterns]))

if HIGH_PRECISION_MODE:
    unique_patterns = [p for p in unique_patterns if p in PATTERN_ALLOWLIST]

for pattern_type in unique_patterns:
    print(f"\n{'=' * 80}")
    print(f"Testing: {pattern_type.upper()}")
    print(f"{'=' * 80}")
    
    # Filter patterns of this type
    pattern_signals = [p for p in quality_patterns if p.get('pattern') == pattern_type]
    
    if not pattern_signals:
        print(f"⚠️  No quality signals for {pattern_type}")
        continue
    
    print(f"Found {len(pattern_signals)} quality signals")
    
    # Create backtest engine for this pattern
    backtest = BacktestEngine(initial_capital=10000, risk_per_trade_pct=1.0)
    
    # Execute trades
    trades_executed = 0

    # Prevent overlapping trades and clustered signals for this pattern
    last_exit_idx = -1
    next_allowed_entry_idx = 0
    
    atr_series = df['atr'] if 'atr' in df.columns else pd.Series([0.0] * len(df))

    for signal in pattern_signals:
        idx = signal.get('index')
        
        if idx is None or idx >= len(df):
            continue

        if idx <= last_exit_idx:
            continue

        if idx < next_allowed_entry_idx:
            continue
        
        entry_candle = df.iloc[idx]
        direction = signal.get('direction', 'bullish')
        atr = _get_atr_value(entry_candle)
        atr_pct = 0.0

        if USE_SESSION_FILTER:
            hour = int(pd.to_datetime(entry_candle['time']).hour)
            if hour < SESSION_START_HOUR or hour > SESSION_END_HOUR:
                continue

        if USE_ATR_FILTER:
            try:
                atr_pct = float(atr_series.rank(pct=True).iloc[idx]) if len(atr_series) else 0.0
            except Exception:
                atr_pct = 0.0
            if atr_pct > ATR_PERCENTILE_MAX:
                continue
        
        # Determine trade direction
        if direction in ['bullish', 'long']:
            trade_direction = 'long'
            entry_price = entry_candle['close']

            if USE_TREND_FILTER and ('ema_20' in entry_candle.index) and ('ema_50' in entry_candle.index):
                if not (entry_candle['ema_20'] > entry_candle['ema_50']):
                    continue

            if USE_RSI_FILTER and ('rsi' in entry_candle.index) and pd.notna(entry_candle['rsi']):
                if float(entry_candle['rsi']) > RSI_LONG_MAX:
                    continue
            
            # Smart stop loss placement
            if 'neckline' in signal:
                stop_loss = signal['neckline'] - (atr * 0.5)
            elif 'support_level' in signal:
                stop_loss = signal['support_level'] - (atr * 0.5)
            elif 'support' in signal:
                stop_loss = signal['support'] - (atr * 0.5)
            else:
                # Use recent low
                lookback = min(20, idx)
                stop_loss = df.iloc[idx-lookback:idx]['low'].min() - (atr * 0.5)
            
            # Calculate risk and reward
            risk = entry_price - stop_loss
            
            # Take profit based on pattern target or risk-reward
            if 'target' in signal:
                take_profit = signal['target']
            else:
                take_profit = entry_price + (risk * 2.0)  # 1:2 RR
        
        else:  # bearish/short
            trade_direction = 'short'
            entry_price = entry_candle['close']

            if USE_TREND_FILTER and ('ema_20' in entry_candle.index) and ('ema_50' in entry_candle.index):
                if not (entry_candle['ema_20'] < entry_candle['ema_50']):
                    continue

            if USE_RSI_FILTER and ('rsi' in entry_candle.index) and pd.notna(entry_candle['rsi']):
                if float(entry_candle['rsi']) < RSI_SHORT_MIN:
                    continue
            
            # Smart stop loss placement
            if 'neckline' in signal:
                stop_loss = signal['neckline'] + (atr * 0.5)
            elif 'resistance_level' in signal:
                stop_loss = signal['resistance_level'] + (atr * 0.5)
            elif 'resistance' in signal:
                stop_loss = signal['resistance'] + (atr * 0.5)
            else:
                # Use recent high
                lookback = min(20, idx)
                stop_loss = df.iloc[idx-lookback:idx]['high'].max() + (atr * 0.5)
            
            risk = stop_loss - entry_price
            
            if 'target' in signal:
                take_profit = signal['target']
            else:
                take_profit = entry_price - (risk * 2.0)  # 1:2 RR
        
        # Validate trade parameters
        if risk <= 0 or pd.isna(risk):
            continue
        
        # Execute trade
        try:
            trade = backtest.simulate_trade(
                direction=trade_direction,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                entry_time=entry_candle['time'],
                df=df
            )
            
            trade['entry_idx'] = int(idx)
            trade['pattern_signal_direction'] = direction
            trade['feature_rsi'] = _safe_float(entry_candle['rsi']) if 'rsi' in entry_candle.index else 0.0
            trade['feature_ema_20'] = _safe_float(entry_candle['ema_20']) if 'ema_20' in entry_candle.index else 0.0
            trade['feature_ema_50'] = _safe_float(entry_candle['ema_50']) if 'ema_50' in entry_candle.index else 0.0
            trade['feature_ema_200'] = _safe_float(entry_candle['ema_200']) if 'ema_200' in entry_candle.index else 0.0
            trade['feature_atr'] = _safe_float(atr)
            trade['feature_atr_percentile'] = _safe_float(atr_pct)
            trade['feature_volume_ratio'] = _safe_float(entry_candle['volume_ratio']) if 'volume_ratio' in entry_candle.index else 0.0
            trade['feature_body'] = _safe_float(entry_candle['body']) if 'body' in entry_candle.index else 0.0
            trade['feature_upper_wick'] = _safe_float(entry_candle['upper_wick']) if 'upper_wick' in entry_candle.index else 0.0
            trade['feature_lower_wick'] = _safe_float(entry_candle['lower_wick']) if 'lower_wick' in entry_candle.index else 0.0
            
            risk_dist = abs(entry_price - stop_loss)
            reward_dist = abs(take_profit - entry_price)
            rr = (reward_dist / risk_dist) if risk_dist > 0 else 0.0
            trade['risk_reward_ratio'] = rr
            if backtest.trades:
                backtest.trades[-1]['risk_reward_ratio'] = rr
                backtest.trades[-1]['entry_idx'] = trade['entry_idx']
                backtest.trades[-1]['pattern_signal_direction'] = trade['pattern_signal_direction']
                backtest.trades[-1]['feature_rsi'] = trade['feature_rsi']
                backtest.trades[-1]['feature_ema_20'] = trade['feature_ema_20']
                backtest.trades[-1]['feature_ema_50'] = trade['feature_ema_50']
                backtest.trades[-1]['feature_ema_200'] = trade['feature_ema_200']
                backtest.trades[-1]['feature_atr'] = trade['feature_atr']
                backtest.trades[-1]['feature_atr_percentile'] = trade['feature_atr_percentile']
                backtest.trades[-1]['feature_volume_ratio'] = trade['feature_volume_ratio']
                backtest.trades[-1]['feature_body'] = trade['feature_body']
                backtest.trades[-1]['feature_upper_wick'] = trade['feature_upper_wick']
                backtest.trades[-1]['feature_lower_wick'] = trade['feature_lower_wick']
            
            exit_idx = int(df[df['time'] == trade['exit_time']].index[0])
            last_exit_idx = exit_idx
            next_allowed_entry_idx = idx + COOLDOWN_BARS
            
            trades_executed += 1
            
            # Print trade result
            outcome = "✅ WIN" if trade['pnl_dollars'] > 0 else "❌ LOSS"
            print(f"  Trade {trades_executed}: {outcome} | {trade['exit_reason']:15s} | P&L: ${trade['pnl_dollars']:7.2f} | RR: {trade.get('risk_reward_ratio', 0):.2f}")
        
        except Exception as e:
            print(f"  ⚠️  Trade error: {e}")
            continue
    
    # Print pattern summary
    print(f"\n{'-' * 80}")
    backtest.print_summary()

    stats = backtest.get_statistics() or {
        'net_profit_pct': 0.0,
        'win_rate': 0.0,
        'profit_factor': 0.0,
        'net_profit': 0.0,
        'max_drawdown_pct': 0.0,
    }
    
    wins = 0
    losses = 0
    rr_values = []
    for t in (backtest.trades or []):
        if t.get('pnl_dollars', 0) > 0:
            wins += 1
        elif t.get('pnl_dollars', 0) < 0:
            losses += 1
        if 'risk_reward_ratio' in t and pd.notna(t.get('risk_reward_ratio')):
            rr_values.append(float(t['risk_reward_ratio']))

    avg_rr = float(pd.Series(rr_values).mean()) if rr_values else 0.0
    
    # Store results
    pattern_results[pattern_type] = {
        'total_signals': len(pattern_signals),
        'trades_executed': trades_executed,
        'wins': wins,
        'losses': losses,
        'avg_rr': avg_rr,
        'total_return': stats.get('net_profit_pct', 0.0),
        'win_rate': stats.get('win_rate', 0.0),
        'profit_factor': stats.get('profit_factor', 0.0),
        'total_pnl': stats.get('net_profit', 0.0),
        'max_drawdown': stats.get('max_drawdown_pct', 0.0),
        'trades': backtest.trades.copy() if backtest.trades else []
    }
    
    # Save individual pattern trades
    if backtest.trades:
        filename = f'logs/backtest_{pattern_type}_trades.csv'
        pd.DataFrame(backtest.trades).to_csv(filename, index=False)
        print(f"✓ Saved to {filename}")

# ==================== COMBINED RESULTS ====================
print("\n" + "=" * 80)
print("COMBINED RESULTS - ALL PATTERNS")
print("=" * 80)

approved_pattern_results = pattern_results
if HIGH_PRECISION_MODE:
    approved_pattern_results = {
        name: res for name, res in pattern_results.items()
        if (res.get('trades_executed', 0) >= MIN_TRADES_FOR_APPROVAL and
            res.get('win_rate', 0.0) >= MIN_WIN_RATE_FOR_APPROVAL and
            res.get('profit_factor', 0.0) >= MIN_PROFIT_FACTOR_FOR_APPROVAL)
    }
    print(f"\nHigh-precision mode: approved {len(approved_pattern_results)}/{len(pattern_results)} patterns")
    if approved_pattern_results:
        print("Approved patterns:")
        for name in sorted(approved_pattern_results.keys()):
            print(f"  - {name}")
    else:
        print("No patterns met approval thresholds. Consider relaxing thresholds.")

# Aggregate all trades
all_trades = []
for pattern_name, results in approved_pattern_results.items():
    for trade in results['trades']:
        trade['pattern'] = pattern_name
        all_trades.append(trade)

if all_trades:
    combined_backtest = BacktestEngine(initial_capital=10000, risk_per_trade_pct=1.0)
    combined_backtest.trades = all_trades
    combined_backtest.capital = 10000
    
    # Recalculate capital progression
    for trade in combined_backtest.trades:
        combined_backtest.capital += trade['pnl_dollars']
    
    print(f"\n📊 Overall Statistics:")
    print(f"{'=' * 80}")
    combined_backtest.print_summary()
    
    # Save all trades
    df_all_trades = pd.DataFrame(all_trades)
    df_all_trades.to_csv('logs/backtest_all_patterns_trades.csv', index=False)
    print(f"\n✓ All trades saved to logs/backtest_all_patterns_trades.csv")

    if EXPORT_ML_DATASET:
        df_ml = df_all_trades.copy()
        df_ml['label_win'] = (df_ml['pnl_dollars'] > 0).astype(int)
        keep_cols = [
            'pattern',
            'direction',
            'pattern_signal_direction',
            'entry_time',
            'exit_time',
            'entry_idx',
            'entry_price',
            'stop_loss',
            'take_profit',
            'risk_reward_ratio',
            'exit_reason',
            'feature_rsi',
            'feature_ema_20',
            'feature_ema_50',
            'feature_ema_200',
            'feature_atr',
            'feature_atr_percentile',
            'feature_volume_ratio',
            'feature_body',
            'feature_upper_wick',
            'feature_lower_wick',
            'label_win',
            'pnl_dollars',
        ]
        keep_cols = [c for c in keep_cols if c in df_ml.columns]
        df_ml = df_ml[keep_cols]
        file_exists = os.path.exists(ML_DATASET_FILENAME)
        df_ml.to_csv(ML_DATASET_FILENAME, index=False, mode='a' if file_exists else 'w', header=not file_exists)
        print(f"✓ ML dataset appended to {ML_DATASET_FILENAME}")

# ==================== PATTERN COMPARISON TABLE ====================
print("\n" + "=" * 80)
print("PATTERN PERFORMANCE COMPARISON")
print("=" * 80)

print(f"\n{'Pattern':<30} {'Signals':>8} {'Trades':>8} {'Win%':>8} {'Return%':>10} {'P.Factor':>10}")
print("-" * 80)

sorted_patterns = sorted(pattern_results.items(), 
                        key=lambda x: x[1]['total_return'], 
                        reverse=True)

if HIGH_PRECISION_MODE:
    sorted_patterns = sorted(approved_pattern_results.items(),
                            key=lambda x: x[1]['total_return'],
                            reverse=True)

for pattern_name, results in sorted_patterns:
    print(f"{pattern_name:<30} "
          f"{results['total_signals']:>8} "
          f"{results['trades_executed']:>8} "
          f"{results['win_rate']:>7.1f}% "
          f"{results['total_return']:>9.2f}% "
          f"{results['profit_factor']:>10.2f}")

# ==================== BEST PATTERNS ====================
print("\n" + "=" * 80)
print("🏆 TOP 5 BEST PERFORMING PATTERNS")
print("=" * 80)

top_5 = sorted_patterns[:5]
for i, (pattern_name, results) in enumerate(top_5, 1):
    print(f"\n{i}. {pattern_name.upper()}")
    print(f"   Return: {results['total_return']:.2f}%")
    print(f"   Win Rate: {results['win_rate']:.1f}%")
    print(f"   Profit Factor: {results['profit_factor']:.2f}")
    print(f"   Total P&L: ${results['total_pnl']:.2f}")

# ==================== RECOMMENDATIONS ====================
print("\n" + "=" * 80)
print("💡 TRADING RECOMMENDATIONS")
print("=" * 80)

# Find patterns with good stats
good_patterns = [
    (name, res) for name, res in approved_pattern_results.items()
    if res['win_rate'] > 50 and res['trades_executed'] >= 3 and res['total_return'] > 0
]

if good_patterns:
    print("\n✅ Patterns worth trading (Win Rate > 50%, Positive Return):")
    for pattern_name, results in sorted(good_patterns, key=lambda x: x[1]['total_return'], reverse=True):
        print(f"  • {pattern_name:30s} - {results['win_rate']:.1f}% win rate, {results['total_return']:+.2f}% return")
else:
    print("\n⚠️  No patterns met the criteria (>50% win rate, positive return)")
    print("   Consider:")
    print("   • Adjusting filters (RSI, volume thresholds)")
    print("   • Testing different timeframes")
    print("   • Refining stop-loss/take-profit ratios")

print("\n" + "=" * 80)
print(f"✅ BACKTEST COMPLETED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)