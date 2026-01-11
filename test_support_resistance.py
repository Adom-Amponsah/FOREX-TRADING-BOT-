from market_data import MarketDataFetcher
from support_resistance import SupportResistanceDetector

fetcher = MarketDataFetcher()
fetcher.connect()
df = fetcher.get_candles(timeframe_minutes=15, num_candles=200)
fetcher.disconnect()

sr_detector = SupportResistanceDetector(df, lookback_candles=150)

support_levels = sr_detector.get_support_levels()
resistance_levels = sr_detector.get_resistance_levels()

print(f"Found {len(support_levels)} support levels:")
for level in support_levels:
    print(f"  Price: {level['price']:.2f} | Touches: {level['touches']} | Strength: {level['strength']}")

print(f"\nFound {len(resistance_levels)} resistance levels:")
for level in resistance_levels:
    print(f"  Price: {level['price']:.2f} | Touches: {level['touches']} | Strength: {level['strength']}")

current_price = df.iloc[-1]['close']
print(f"\nCurrent price: {current_price:.2f}")

at_support, support_info = sr_detector.is_at_support(current_price)
at_resistance, resistance_info = sr_detector.is_at_resistance(current_price)

if at_support:
    print(f"✓ NEAR SUPPORT at {support_info['price']:.2f} (strength: {support_info['strength']})")
if at_resistance:
    print(f"✓ NEAR RESISTANCE at {resistance_info['price']:.2f} (strength: {resistance_info['strength']})")
