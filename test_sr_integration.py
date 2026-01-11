from market_data import MarketDataFetcher
from pattern_detector import PatternDetector

fetcher = MarketDataFetcher()
fetcher.connect()
df = fetcher.get_candles(timeframe_minutes=15, num_candles=500)
fetcher.disconnect()

detector = PatternDetector(df)

raw = detector.detect_bullish_engulfing()
filtered = detector.detect_bullish_engulfing_filtered()
sr_confirmed = detector.detect_bullish_engulfing_with_SR()

print(f"Signal Funnel:")
print(f"  Raw patterns: {len(raw)}")
if len(raw) > 0:
    print(f"  After filters: {len(filtered)} ({100*len(filtered)/len(raw):.0f}%)")
    print(f"  After S/R check: {len(sr_confirmed)} ({100*len(sr_confirmed)/len(raw):.0f}%)")
else:
    print(f"  After filters: {len(filtered)}")
    print(f"  After S/R check: {len(sr_confirmed)}")

print(f"\nHigh-quality signals (with S/R):")
for signal in sr_confirmed:
    print(f"  Index {signal['index']}: Price {signal['price']:.2f} at support {signal['support_level']:.2f} (strength {signal['support_strength']})")
