from market_data import MarketDataFetcher
from pattern_detector import PatternDetector
from visualizer import ChartVisualizer

fetcher = MarketDataFetcher()
fetcher.connect()
df = fetcher.get_candles(timeframe_minutes=15, num_candles=300)
fetcher.disconnect()

detector = PatternDetector(df)
bullish = detector.detect_bullish_engulfing()
bearish = detector.detect_bearish_engulfing()

viz = ChartVisualizer()
viz.plot_with_signals(df, bullish, bearish, title="Gold - Engulfing Patterns")
