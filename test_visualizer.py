from market_data import MarketDataFetcher
from visualizer import ChartVisualizer

fetcher = MarketDataFetcher()
fetcher.connect()
df = fetcher.get_candles(timeframe_minutes=15, num_candles=100)
fetcher.disconnect()

viz = ChartVisualizer()
viz.plot_candles(df, title="Gold 15-Minute Chart", save_path="logs/gold_chart.png")
