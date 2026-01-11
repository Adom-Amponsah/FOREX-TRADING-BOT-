import pandas as pd
import numpy as np
import pandas_ta as ta

class PatternDetector:
    """Detects technical analysis patterns in OHLC data"""
    
    def __init__(self, df):
        """
        Args:
            df: DataFrame with columns: time, open, high, low, close, volume
        """
        self.df = df.copy()
        self.df.reset_index(drop=True, inplace=True)
        self._calculate_indicators()
        
    def _calculate_indicators(self):
        """Calculate technical indicators"""
        self.df['rsi'] = ta.rsi(self.df['close'], length=14)
        
        self.df['ema_50'] = ta.ema(self.df['close'], length=50)
        self.df['ema_200'] = ta.ema(self.df['close'], length=200)
        
        self.df['atr'] = ta.atr(self.df['high'], self.df['low'], self.df['close'], length=14)
        
        self.df['volume_ma'] = self.df['volume'].rolling(window=20).mean()
        
        print("✓ Technical indicators calculated")
        
    def detect_bullish_engulfing(self, min_body_ratio=1.5):
        """
        Detect bullish engulfing patterns
        
        Args:
            min_body_ratio: Current candle body must be this times larger than previous
            
        Returns:
            List of indices where pattern detected
        """
        signals = []
        
        for i in range(1, len(self.df)):
            prev = self.df.iloc[i-1]
            curr = self.df.iloc[i]
            
            prev_body = abs(prev['close'] - prev['open'])
            curr_body = abs(curr['close'] - curr['open'])
            
            prev_is_red = prev['close'] < prev['open']
            
            curr_is_green = curr['close'] > curr['open']
            
            curr_open_below_prev_close = curr['open'] < prev['close']
            curr_close_above_prev_open = curr['close'] > prev['open']
            
            body_ratio_ok = curr_body > (prev_body * min_body_ratio) if prev_body > 0 else False
            
            if (prev_is_red and 
                curr_is_green and 
                curr_open_below_prev_close and 
                curr_close_above_prev_open and
                body_ratio_ok):
                
                signals.append(i)
        
        return signals
    
    def detect_bearish_engulfing(self, min_body_ratio=1.5):
        """
        Detect bearish engulfing patterns
        (opposite of bullish)
        """
        signals = []
        
        for i in range(1, len(self.df)):
            prev = self.df.iloc[i-1]
            curr = self.df.iloc[i]
            
            prev_body = abs(prev['close'] - prev['open'])
            curr_body = abs(curr['close'] - curr['open'])
            
            prev_is_green = prev['close'] > prev['open']
            curr_is_red = curr['close'] < curr['open']
            
            curr_open_above_prev_close = curr['open'] > prev['close']
            curr_close_below_prev_open = curr['close'] < prev['open']
            
            body_ratio_ok = curr_body > (prev_body * min_body_ratio) if prev_body > 0 else False
            
            if (prev_is_green and 
                curr_is_red and 
                curr_open_above_prev_close and 
                curr_close_below_prev_open and
                body_ratio_ok):
                
                signals.append(i)
        
        return signals
    
    def detect_bullish_engulfing_filtered(self, min_body_ratio=1.5):
        """
        Bullish engulfing with quality filters
        """
        raw_signals = self.detect_bullish_engulfing(min_body_ratio)
        filtered_signals = []
        
        for idx in raw_signals:
            candle = self.df.iloc[idx]
            
            if pd.isna(candle['rsi']) or candle['rsi'] > 40:
                continue
            
            if pd.isna(candle['ema_50']) or candle['close'] > candle['ema_50']:
                continue
            
            if pd.isna(candle['volume_ma']) or candle['volume'] < candle['volume_ma']:
                continue
            
            filtered_signals.append(idx)
        
        return filtered_signals
    
    def detect_bearish_engulfing_filtered(self, min_body_ratio=1.5):
        """
        Bearish engulfing with quality filters
        """
        raw_signals = self.detect_bearish_engulfing(min_body_ratio)
        filtered_signals = []
        
        for idx in raw_signals:
            candle = self.df.iloc[idx]
            
            if pd.isna(candle['rsi']) or candle['rsi'] < 60:
                continue
            
            if pd.isna(candle['ema_50']) or candle['close'] < candle['ema_50']:
                continue
            
            if pd.isna(candle['volume_ma']) or candle['volume'] < candle['volume_ma']:
                continue
            
            filtered_signals.append(idx)
        
        return filtered_signals
    
    def get_pattern_details(self, index):
        """Get details of candle at index"""
        candle = self.df.iloc[index]
        prev_candle = self.df.iloc[index-1] if index > 0 else None
        
        details = {
            'time': candle['time'],
            'open': candle['open'],
            'high': candle['high'],
            'low': candle['low'],
            'close': candle['close'],
            'body_size': abs(candle['close'] - candle['open']),
            'is_green': candle['close'] > candle['open']
        }
        
        if prev_candle is not None:
            details['prev_body_size'] = abs(prev_candle['close'] - prev_candle['open'])
            details['body_ratio'] = details['body_size'] / details['prev_body_size'] if details['prev_body_size'] > 0 else 0
        
        return details
    
    def detect_bullish_engulfing_with_SR(self, min_body_ratio=1.5):
        """Bullish engulfing that appears AT SUPPORT"""
        from support_resistance import SupportResistanceDetector
        
        filtered_signals = self.detect_bullish_engulfing_filtered(min_body_ratio)
        
        sr_detector = SupportResistanceDetector(self.df, lookback_candles=150)
        
        sr_confirmed = []
        
        for idx in filtered_signals:
            candle = self.df.iloc[idx]
            price = candle['close']
            
            at_support, support_info = sr_detector.is_at_support(price, tolerance_pct=0.3)
            
            if at_support and support_info['strength'] >= 2:
                sr_confirmed.append({
                    'index': idx,
                    'price': price,
                    'support_level': support_info['price'],
                    'support_strength': support_info['strength']
                })
        
        return sr_confirmed
    
    def detect_bearish_engulfing_with_SR(self, min_body_ratio=1.5):
        """Bearish engulfing that appears AT RESISTANCE"""
        from support_resistance import SupportResistanceDetector
        
        filtered_signals = self.detect_bearish_engulfing_filtered(min_body_ratio)
        
        sr_detector = SupportResistanceDetector(self.df, lookback_candles=150)
        sr_confirmed = []
        
        for idx in filtered_signals:
            candle = self.df.iloc[idx]
            price = candle['close']
            
            at_resistance, resistance_info = sr_detector.is_at_resistance(price, tolerance_pct=0.3)
            
            if at_resistance and resistance_info['strength'] >= 2:
                sr_confirmed.append({
                    'index': idx,
                    'price': price,
                    'resistance_level': resistance_info['price'],
                    'resistance_strength': resistance_info['strength']
                })
        
        return sr_confirmed
