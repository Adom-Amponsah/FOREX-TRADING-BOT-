from market_data import MarketDataFetcher

fetcher = MarketDataFetcher(symbol="XAUUSD")

if fetcher.connect():
    
    df_15min = fetcher.get_candles(timeframe_minutes=15, num_candles=200)
    print("\n15-Minute Data:")
    print(df_15min.tail())
    
    df_1hour = fetcher.get_candles(timeframe_minutes=60, num_candles=100)
    print("\n1-Hour Data:")
    print(df_1hour.tail())
    
    current = fetcher.get_current_price()
    print(f"\nCurrent Price:")
    print(f"  Bid: {current['bid']}")
    print(f"  Ask: {current['ask']}")
    print(f"  Spread: {current['spread']}")
    
    fetcher.disconnect()
else:
    print("Failed to connect to MT5")
