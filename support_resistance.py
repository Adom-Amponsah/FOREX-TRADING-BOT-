import pandas as pd
import numpy as np

class SupportResistanceDetector:
    """Identifies key support and resistance levels"""
    
    def __init__(self, df, lookback_candles=100):
        """
        Args:
            df: OHLC DataFrame
            lookback_candles: How far back to scan for levels
        """
        self.df = df.tail(lookback_candles).copy()
        self.df.reset_index(drop=True, inplace=True)
        
    def find_swing_highs(self, window=5):
        """
        Find swing high points (local maxima)
        
        Args:
            window: Look N candles left and right
            
        Returns:
            List of (index, price) tuples
        """
        swing_highs = []
        
        for i in range(window, len(self.df) - window):
            current_high = self.df.iloc[i]['high']
            
            is_swing_high = True
            for j in range(i - window, i + window + 1):
                if j != i and self.df.iloc[j]['high'] >= current_high:
                    is_swing_high = False
                    break
            
            if is_swing_high:
                swing_highs.append((i, current_high))
        
        return swing_highs
    
    def find_swing_lows(self, window=5):
        """Find swing low points (local minima)"""
        swing_lows = []
        
        for i in range(window, len(self.df) - window):
            current_low = self.df.iloc[i]['low']
            
            is_swing_low = True
            for j in range(i - window, i + window + 1):
                if j != i and self.df.iloc[j]['low'] <= current_low:
                    is_swing_low = False
                    break
            
            if is_swing_low:
                swing_lows.append((i, current_low))
        
        return swing_lows
    
    def cluster_levels(self, swing_points, tolerance_pct=0.2):
        """
        Group nearby swing points into zones
        
        Args:
            swing_points: List of (index, price) tuples
            tolerance_pct: Price levels within this % are same zone
            
        Returns:
            List of support/resistance zones
        """
        if not swing_points:
            return []
        
        sorted_points = sorted(swing_points, key=lambda x: x[1])
        
        zones = []
        current_zone = [sorted_points[0][1]]
        
        for i in range(1, len(sorted_points)):
            price = sorted_points[i][1]
            zone_avg = np.mean(current_zone)
            
            if abs(price - zone_avg) / zone_avg <= (tolerance_pct / 100):
                current_zone.append(price)
            else:
                zones.append({
                    'price': np.mean(current_zone),
                    'touches': len(current_zone),
                    'strength': len(current_zone)
                })
                current_zone = [price]
        
        zones.append({
            'price': np.mean(current_zone),
            'touches': len(current_zone),
            'strength': len(current_zone)
        })
        
        zones = [z for z in zones if z['touches'] >= 2]
        
        return zones
    
    def get_support_levels(self):
        """Get all support levels (from swing lows)"""
        swing_lows = self.find_swing_lows(window=5)
        return self.cluster_levels(swing_lows, tolerance_pct=0.2)
    
    def get_resistance_levels(self):
        """Get all resistance levels (from swing highs)"""
        swing_highs = self.find_swing_highs(window=5)
        return self.cluster_levels(swing_highs, tolerance_pct=0.2)
    
    def is_at_support(self, current_price, tolerance_pct=0.3):
        """Check if current price is near a support level"""
        support_levels = self.get_support_levels()
        
        for level in support_levels:
            if abs(current_price - level['price']) / level['price'] <= (tolerance_pct / 100):
                return True, level
        
        return False, None
    
    def is_at_resistance(self, current_price, tolerance_pct=0.3):
        """Check if current price is near a resistance level"""
        resistance_levels = self.get_resistance_levels()
        
        for level in resistance_levels:
            if abs(current_price - level['price']) / level['price'] <= (tolerance_pct / 100):
                return True, level
        
        return False, None
