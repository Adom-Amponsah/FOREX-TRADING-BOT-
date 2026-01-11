from market_data import MarketDataFetcher
from pattern_detector import PatternDetector

fetcher = MarketDataFetcher()
fetcher.connect()
df = fetcher.get_candles(timeframe_minutes=15, num_candles=500)
fetcher.disconnect()

detector = PatternDetector(df)

bullish_raw = detector.detect_bullish_engulfing()
print(f"Bullish engulfing (raw): {len(bullish_raw)}")

bullish_filtered = detector.detect_bullish_engulfing_filtered()
print(f"Bullish engulfing (filtered): {len(bullish_filtered)}")

if len(bullish_raw) > 0:
    reduction = 100 * (1 - len(bullish_filtered)/len(bullish_raw))
    print(f"\nFilter reduced signals by {reduction:.1f}%")
else:
    print("\nNo raw signals found to filter")
