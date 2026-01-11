from market_data import MarketDataFetcher
from pattern_detector import PatternDetector
from backtest_engine import BacktestEngine
import pandas as pd

print("Fetching data for optimization...")
fetcher = MarketDataFetcher()
fetcher.connect()
df = fetcher.get_candles(timeframe_minutes=15, num_candles=2000)
fetcher.disconnect()

body_ratios = [1.3, 1.5, 1.7, 2.0]
reward_risks = [1.5, 2.0, 2.5, 3.0]
risk_pcts = [0.5, 1.0, 1.5, 2.0]

results = []

print("Testing parameter combinations...\n")

total_combinations = len(body_ratios) * len(reward_risks) * len(risk_pcts)
current = 0

for body_ratio in body_ratios:
    for rr_ratio in reward_risks:
        for risk_pct in risk_pcts:
            current += 1
            print(f"Testing combination {current}/{total_combinations}...", end='\r')
            
            detector = PatternDetector(df)
            signals = detector.detect_bullish_engulfing_with_SR(min_body_ratio=body_ratio)
            
            if len(signals) == 0:
                continue
            
            backtest = BacktestEngine(initial_capital=10000, risk_per_trade_pct=risk_pct)
            
            for signal in signals:
                idx = signal['index']
                entry_candle = df.iloc[idx]
                
                entry_price = entry_candle['close']
                stop_loss = entry_candle['low'] - 2
                risk = entry_price - stop_loss
                take_profit = entry_price + (risk * rr_ratio)
                
                backtest.simulate_trade('long', entry_price, stop_loss, take_profit, entry_candle['time'], df)
            
            stats = backtest.get_statistics()
            
            if stats and stats['total_trades'] >= 5:
                results.append({
                    'body_ratio': body_ratio,
                    'rr_ratio': rr_ratio,
                    'risk_pct': risk_pct,
                    'total_trades': stats['total_trades'],
                    'win_rate': stats['win_rate'],
                    'profit_factor': stats['profit_factor'],
                    'net_profit_pct': stats['net_profit_pct'],
                    'max_drawdown': stats['max_drawdown_pct']
                })

print("\n\nOptimization complete!")

results_df = pd.DataFrame(results)
results_df = results_df.sort_values('profit_factor', ascending=False)

print("\nTop 10 Parameter Combinations:")
print(results_df.head(10).to_string(index=False))

results_df.to_csv('logs/optimization_results.csv', index=False)
print("\n✓ Full results saved to logs/optimization_results.csv")
