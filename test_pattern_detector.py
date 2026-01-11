from market_data import MarketDataFetcher
from pattern_detector import PatternDetector

print("Fetching data...")
fetcher = MarketDataFetcher()
fetcher.connect()
df = fetcher.get_candles(timeframe_minutes=15, num_candles=500)
fetcher.disconnect()

print("\nDetecting bullish engulfing patterns...")
detector = PatternDetector(df)
bullish_signals = detector.detect_bullish_engulfing(min_body_ratio=1.5)

print(f"Found {len(bullish_signals)} bullish engulfing patterns")

for idx in bullish_signals:
    details = detector.get_pattern_details(idx)
    print(f"\nPattern at index {idx}:")
    print(f"  Time: {details['time']}")
    print(f"  Price: {details['close']:.2f}")
    print(f"  Body ratio: {details.get('body_ratio', 0):.2f}x")

print("\nDetecting bearish engulfing patterns...")
bearish_signals = detector.detect_bearish_engulfing(min_body_ratio=1.5)
print(f"Found {len(bearish_signals)} bearish engulfing patterns")
