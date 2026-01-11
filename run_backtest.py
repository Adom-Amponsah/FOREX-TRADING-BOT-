from market_data import MarketDataFetcher
from pattern_detector import PatternDetector
from backtest_engine import BacktestEngine
import pandas as pd

print("Fetching historical data...")
fetcher = MarketDataFetcher()
fetcher.connect()
df = fetcher.get_candles(timeframe_minutes=15, num_candles=2000)
fetcher.disconnect()

print(f"Loaded {len(df)} candles from {df.iloc[0]['time']} to {df.iloc[-1]['time']}")

print("\nDetecting patterns with all filters...")
detector = PatternDetector(df)
bullish_signals = detector.detect_bullish_engulfing_with_SR()

print(f"Found {len(bullish_signals)} high-quality bullish engulfing setups")

backtest = BacktestEngine(initial_capital=10000, risk_per_trade_pct=1.0)

print("\nSimulating trades...")
for signal in bullish_signals:
    idx = signal['index']
    entry_candle = df.iloc[idx]
    
    direction = 'long'
    entry_price = entry_candle['close']
    
    stop_loss = entry_candle['low'] - 2
    
    risk = entry_price - stop_loss
    take_profit = entry_price + (risk * 2)
    
    trade = backtest.simulate_trade(
        direction=direction,
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        entry_time=entry_candle['time'],
        df=df
    )
    
    print(f"  Trade {len(backtest.trades)}: {trade['exit_reason']} | P&L: ${trade['pnl_dollars']:.2f}")

backtest.print_summary()

if backtest.trades:
    pd.DataFrame(backtest.trades).to_csv('logs/backtest_trades.csv', index=False)
    print("\n✓ Trade log saved to logs/backtest_trades.csv")
