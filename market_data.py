import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta

class MarketDataFetcher:
    """Handles all MT5 data fetching operations"""
    
    def __init__(self, symbol="XAUUSD"):
        self.symbol = symbol
        self.connected = False
        
    def connect(self):
        """Initialize MT5 connection"""
        if not mt5.initialize():
            print("ERROR: MT5 initialization failed")
            return False
            
        if not mt5.symbol_select(self.symbol, True):
            print(f"ERROR: Failed to select {self.symbol}")
            mt5.shutdown()
            return False
            
        self.connected = True
        print(f"✓ Connected to MT5, {self.symbol} ready")
        return True
    
    def disconnect(self):
        """Close MT5 connection"""
        mt5.shutdown()
        self.connected = False
        print("✓ MT5 connection closed")
    
    def get_candles(self, timeframe_minutes=15, num_candles=200):
        """
        Fetch historical candles
        
        Args:
            timeframe_minutes: 1, 5, 15, 30, 60, 240 (4H), 1440 (D1)
            num_candles: How many candles to fetch
            
        Returns:
            pandas DataFrame with OHLC data
        """
        if not self.connected:
            print("ERROR: Not connected to MT5")
            return None
        
        timeframe_map = {
            1: mt5.TIMEFRAME_M1,
            5: mt5.TIMEFRAME_M5,
            15: mt5.TIMEFRAME_M15,
            30: mt5.TIMEFRAME_M30,
            60: mt5.TIMEFRAME_H1,
            240: mt5.TIMEFRAME_H4,
            1440: mt5.TIMEFRAME_D1
        }
        
        if timeframe_minutes not in timeframe_map:
            print(f"ERROR: Invalid timeframe {timeframe_minutes}")
            return None
        
        timeframe = timeframe_map[timeframe_minutes]
        
        rates = mt5.copy_rates_from_pos(self.symbol, timeframe, 0, num_candles)
        
        if rates is None or len(rates) == 0:
            print("ERROR: No data received from MT5")
            return None
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        df = df.rename(columns={
            'tick_volume': 'volume'
        })
        
        df = df[['time', 'open', 'high', 'low', 'close', 'volume']]
        
        print(f"✓ Fetched {len(df)} candles ({timeframe_minutes}min timeframe)")
        return df
    
    def get_current_price(self):
        """Get current bid/ask prices"""
        if not self.connected:
            print("ERROR: Not connected to MT5")
            return None
        
        symbol_info = mt5.symbol_info(self.symbol)
        
        return {
            'time': datetime.now(),
            'bid': symbol_info.bid,
            'ask': symbol_info.ask,
            'spread': symbol_info.spread
        }
