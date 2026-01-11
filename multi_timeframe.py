from market_data import MarketDataFetcher

class MultiTimeframeAnalyzer:
    """Analyze patterns across multiple timeframes"""
    
    def __init__(self):
        self.fetcher = MarketDataFetcher()
    
    def check_higher_timeframe_trend(self, current_time, timeframe_min=60):
        """
        Check if higher timeframe confirms the setup
        
        Args:
            current_time: Time of pattern on lower timeframe
            timeframe_min: Higher timeframe to check (60 = 1 hour, 240 = 4 hour)
            
        Returns:
            'uptrend', 'downtrend', or 'neutral'
        """
        self.fetcher.connect()
        df_higher = self.fetcher.get_candles(timeframe_minutes=timeframe_min, num_candles=100)
        self.fetcher.disconnect()
        
        df_higher['ema_20'] = df_higher['close'].ewm(span=20).mean()
        df_higher['ema_50'] = df_higher['close'].ewm(span=50).mean()
        
        latest = df_higher.iloc[-1]
        
        if latest['close'] > latest['ema_20'] and latest['ema_20'] > latest['ema_50']:
            return 'uptrend'
        elif latest['close'] < latest['ema_20'] and latest['ema_20'] < latest['ema_50']:
            return 'downtrend'
        else:
            return 'neutral'
