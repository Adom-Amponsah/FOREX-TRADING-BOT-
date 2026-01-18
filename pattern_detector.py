import pandas as pd
import numpy as np
import pandas_ta_classic as ta

class PatternDetector:
    """
    Comprehensive technical analysis pattern detector
    Implements 11 major chart patterns from forex.com
    """
    
    def __init__(self, df):
        """
        Args:
            df: DataFrame with columns: time, open, high, low, close, volume
        """
        self.df = df.copy()
        self.df.reset_index(drop=True, inplace=True)
        self._calculate_indicators()
        
    def _calculate_indicators(self):
        """Calculate technical indicators needed for pattern detection"""
        # RSI for overbought/oversold conditions
        self.df['rsi'] = ta.rsi(self.df['close'], length=14)
        
        # EMAs for trend context
        self.df['ema_20'] = ta.ema(self.df['close'], length=20)
        self.df['ema_50'] = ta.ema(self.df['close'], length=50)
        self.df['ema_200'] = ta.ema(self.df['close'], length=200)
        
        # ATR for volatility measurement
        self.df['atr'] = ta.atr(self.df['high'], self.df['low'], self.df['close'], length=14)
        
        # Volume indicators
        self.df['volume_ma'] = self.df['volume'].rolling(window=20).mean()
        self.df['volume_ratio'] = self.df['volume'] / self.df['volume_ma']
        
        # Candle body and wick calculations
        self.df['body'] = abs(self.df['close'] - self.df['open'])
        self.df['upper_wick'] = self.df['high'] - self.df[['open', 'close']].max(axis=1)
        self.df['lower_wick'] = self.df[['open', 'close']].min(axis=1) - self.df['low']
        
        print("✓ Technical indicators calculated successfully")
        
    # ==================== ENGULFING PATTERNS ====================
    
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
            
            # Pattern conditions
            prev_is_red = prev['close'] < prev['open']
            curr_is_green = curr['close'] > curr['open']
            curr_open_below_prev_close = curr['open'] <= prev['close']
            curr_close_above_prev_open = curr['close'] >= prev['open']
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
        """
        signals = []
        
        for i in range(1, len(self.df)):
            prev = self.df.iloc[i-1]
            curr = self.df.iloc[i]
            
            prev_body = abs(prev['close'] - prev['open'])
            curr_body = abs(curr['close'] - curr['open'])
            
            # Pattern conditions
            prev_is_green = prev['close'] > prev['open']
            curr_is_red = curr['close'] < curr['open']
            curr_open_above_prev_close = curr['open'] >= prev['close']
            curr_close_below_prev_open = curr['close'] <= prev['open']
            body_ratio_ok = curr_body > (prev_body * min_body_ratio) if prev_body > 0 else False
            
            if (prev_is_green and 
                curr_is_red and 
                curr_open_above_prev_close and 
                curr_close_below_prev_open and
                body_ratio_ok):
                signals.append(i)
        
        return signals
    
    # ==================== TRIANGLE PATTERNS ====================
    
    def detect_ascending_triangle(self, lookback=20, tolerance=0.002):
        """
        Ascending Triangle: Horizontal resistance + ascending support
        Bullish continuation pattern
        
        Args:
            lookback: Number of candles to analyze
            tolerance: Price tolerance for horizontal line (0.2%)
        """
        signals = []
        
        for i in range(lookback, len(self.df)):
            window = self.df.iloc[i-lookback:i]
            
            # Find swing highs and lows
            highs = []
            lows = []
            
            for j in range(1, len(window)-1):
                if (window.iloc[j]['high'] > window.iloc[j-1]['high'] and 
                    window.iloc[j]['high'] > window.iloc[j+1]['high']):
                    highs.append((j, window.iloc[j]['high']))
                    
                if (window.iloc[j]['low'] < window.iloc[j-1]['low'] and 
                    window.iloc[j]['low'] < window.iloc[j+1]['low']):
                    lows.append((j, window.iloc[j]['low']))
            
            if len(highs) >= 2 and len(lows) >= 2:
                # Check for horizontal resistance
                high_prices = [h[1] for h in highs]
                resistance_level = np.mean(high_prices)
                horizontal_resistance = all(abs(h - resistance_level) / resistance_level < tolerance for h in high_prices)
                
                # Check for ascending support
                low_indices = [l[0] for l in lows]
                low_prices = [l[1] for l in lows]
                
                if len(low_prices) >= 2:
                    # Linear regression for support line
                    slope, _ = np.polyfit(low_indices, low_prices, 1)
                    ascending_support = slope > 0
                    
                    if horizontal_resistance and ascending_support:
                        current_price = self.df.iloc[i]['close']
                        
                        # Breakout confirmation
                        if current_price > resistance_level:
                            signals.append({
                                'index': i,
                                'pattern': 'ascending_triangle',
                                'resistance': resistance_level,
                                'breakout_price': current_price,
                                'direction': 'bullish'
                            })
        
        return signals
    
    def detect_descending_triangle(self, lookback=20, tolerance=0.002):
        """
        Descending Triangle: Horizontal support + descending resistance
        Bearish continuation pattern
        """
        signals = []
        
        for i in range(lookback, len(self.df)):
            window = self.df.iloc[i-lookback:i]
            
            # Find swing highs and lows
            highs = []
            lows = []
            
            for j in range(1, len(window)-1):
                if (window.iloc[j]['high'] > window.iloc[j-1]['high'] and 
                    window.iloc[j]['high'] > window.iloc[j+1]['high']):
                    highs.append((j, window.iloc[j]['high']))
                    
                if (window.iloc[j]['low'] < window.iloc[j-1]['low'] and 
                    window.iloc[j]['low'] < window.iloc[j+1]['low']):
                    lows.append((j, window.iloc[j]['low']))
            
            if len(highs) >= 2 and len(lows) >= 2:
                # Check for horizontal support
                low_prices = [l[1] for l in lows]
                support_level = np.mean(low_prices)
                horizontal_support = all(abs(l - support_level) / support_level < tolerance for l in low_prices)
                
                # Check for descending resistance
                high_indices = [h[0] for h in highs]
                high_prices = [h[1] for h in highs]
                
                if len(high_prices) >= 2:
                    slope, _ = np.polyfit(high_indices, high_prices, 1)
                    descending_resistance = slope < 0
                    
                    if horizontal_support and descending_resistance:
                        current_price = self.df.iloc[i]['close']
                        
                        # Breakout confirmation
                        if current_price < support_level:
                            signals.append({
                                'index': i,
                                'pattern': 'descending_triangle',
                                'support': support_level,
                                'breakout_price': current_price,
                                'direction': 'bearish'
                            })
        
        return signals
    
    def detect_symmetrical_triangle(self, lookback=20):
        """
        Symmetrical Triangle: Converging support and resistance
        Continuation pattern (direction depends on breakout)
        """
        signals = []
        
        for i in range(lookback, len(self.df)):
            window = self.df.iloc[i-lookback:i]
            
            # Find swing highs and lows
            highs = []
            lows = []
            
            for j in range(1, len(window)-1):
                if (window.iloc[j]['high'] > window.iloc[j-1]['high'] and 
                    window.iloc[j]['high'] > window.iloc[j+1]['high']):
                    highs.append((j, window.iloc[j]['high']))
                    
                if (window.iloc[j]['low'] < window.iloc[j-1]['low'] and 
                    window.iloc[j]['low'] < window.iloc[j+1]['low']):
                    lows.append((j, window.iloc[j]['low']))
            
            if len(highs) >= 2 and len(lows) >= 2:
                high_indices = [h[0] for h in highs]
                high_prices = [h[1] for h in highs]
                low_indices = [l[0] for l in lows]
                low_prices = [l[1] for l in lows]
                
                # Calculate slopes
                resistance_slope, resistance_intercept = np.polyfit(high_indices, high_prices, 1)
                support_slope, support_intercept = np.polyfit(low_indices, low_prices, 1)
                
                # Converging lines (resistance descending, support ascending)
                if resistance_slope < 0 and support_slope > 0:
                    current_price = self.df.iloc[i]['close']
                    
                    # Calculate projected resistance and support
                    resistance_at_current = resistance_slope * (lookback - 1) + resistance_intercept
                    support_at_current = support_slope * (lookback - 1) + support_intercept
                    
                    # Check for breakout
                    if current_price > resistance_at_current:
                        signals.append({
                            'index': i,
                            'pattern': 'symmetrical_triangle',
                            'breakout_price': current_price,
                            'direction': 'bullish'
                        })
                    elif current_price < support_at_current:
                        signals.append({
                            'index': i,
                            'pattern': 'symmetrical_triangle',
                            'breakout_price': current_price,
                            'direction': 'bearish'
                        })
        
        return signals
    
    # ==================== FLAG PATTERNS ====================
    
    def detect_bull_flag(self, lookback=10, pole_strength=0.02):
        """
        Bull Flag: Strong uptrend followed by slight downward consolidation
        
        Args:
            lookback: Candles for flag formation
            pole_strength: Minimum % gain for the pole (2%)
        """
        signals = []
        
        for i in range(lookback + 10, len(self.df)):
            # Check for strong upward pole (previous 5-10 candles)
            pole_start = i - lookback - 10
            pole_end = i - lookback
            
            pole_data = self.df.iloc[pole_start:pole_end]
            pole_gain = (pole_data.iloc[-1]['close'] - pole_data.iloc[0]['close']) / pole_data.iloc[0]['close']
            
            if pole_gain > pole_strength:
                # Check for flag (consolidation with slight downward slope)
                flag_data = self.df.iloc[pole_end:i]
                
                flag_highs = flag_data['high'].values
                flag_lows = flag_data['low'].values
                flag_indices = np.arange(len(flag_data))
                
                # Flag should have parallel or slightly converging trendlines
                high_slope, _ = np.polyfit(flag_indices, flag_highs, 1)
                low_slope, _ = np.polyfit(flag_indices, flag_lows, 1)
                
                # Both slopes should be negative or flat (consolidation)
                if high_slope <= 0 and low_slope <= 0:
                    current_price = self.df.iloc[i]['close']
                    flag_resistance = flag_data['high'].max()
                    
                    # Breakout above flag resistance
                    if current_price > flag_resistance:
                        signals.append({
                            'index': i,
                            'pattern': 'bull_flag',
                            'pole_gain': pole_gain,
                            'breakout_price': current_price,
                            'direction': 'bullish'
                        })
        
        return signals
    
    def detect_bear_flag(self, lookback=10, pole_strength=0.02):
        """
        Bear Flag: Strong downtrend followed by slight upward consolidation
        """
        signals = []
        
        for i in range(lookback + 10, len(self.df)):
            # Check for strong downward pole
            pole_start = i - lookback - 10
            pole_end = i - lookback
            
            pole_data = self.df.iloc[pole_start:pole_end]
            pole_loss = (pole_data.iloc[0]['close'] - pole_data.iloc[-1]['close']) / pole_data.iloc[0]['close']
            
            if pole_loss > pole_strength:
                # Check for flag (upward consolidation)
                flag_data = self.df.iloc[pole_end:i]
                
                flag_highs = flag_data['high'].values
                flag_lows = flag_data['low'].values
                flag_indices = np.arange(len(flag_data))
                
                high_slope, _ = np.polyfit(flag_indices, flag_highs, 1)
                low_slope, _ = np.polyfit(flag_indices, flag_lows, 1)
                
                # Both slopes should be positive (upward consolidation)
                if high_slope >= 0 and low_slope >= 0:
                    current_price = self.df.iloc[i]['close']
                    flag_support = flag_data['low'].min()
                    
                    # Breakout below flag support
                    if current_price < flag_support:
                        signals.append({
                            'index': i,
                            'pattern': 'bear_flag',
                            'pole_loss': pole_loss,
                            'breakout_price': current_price,
                            'direction': 'bearish'
                        })
        
        return signals
    
    # ==================== WEDGE PATTERNS ====================
    
    def detect_rising_wedge(self, lookback=20):
        """
        Rising Wedge: Both support and resistance ascending, converging
        Bearish reversal pattern
        """
        signals = []
        
        for i in range(lookback, len(self.df)):
            window = self.df.iloc[i-lookback:i]
            
            highs = []
            lows = []
            
            for j in range(1, len(window)-1):
                if (window.iloc[j]['high'] > window.iloc[j-1]['high'] and 
                    window.iloc[j]['high'] > window.iloc[j+1]['high']):
                    highs.append((j, window.iloc[j]['high']))
                    
                if (window.iloc[j]['low'] < window.iloc[j-1]['low'] and 
                    window.iloc[j]['low'] < window.iloc[j+1]['low']):
                    lows.append((j, window.iloc[j]['low']))
            
            if len(highs) >= 2 and len(lows) >= 2:
                high_indices = [h[0] for h in highs]
                high_prices = [h[1] for h in highs]
                low_indices = [l[0] for l in lows]
                low_prices = [l[1] for l in lows]
                
                resistance_slope, resistance_intercept = np.polyfit(high_indices, high_prices, 1)
                support_slope, support_intercept = np.polyfit(low_indices, low_prices, 1)
                
                # Both ascending, support rising faster (converging)
                if resistance_slope > 0 and support_slope > 0 and support_slope > resistance_slope:
                    current_price = self.df.iloc[i]['close']
                    support_at_current = support_slope * (lookback - 1) + support_intercept
                    
                    # Breakout below support
                    if current_price < support_at_current:
                        signals.append({
                            'index': i,
                            'pattern': 'rising_wedge',
                            'breakout_price': current_price,
                            'direction': 'bearish'
                        })
        
        return signals
    
    def detect_falling_wedge(self, lookback=20):
        """
        Falling Wedge: Both support and resistance descending, converging
        Bullish reversal pattern
        """
        signals = []
        
        for i in range(lookback, len(self.df)):
            window = self.df.iloc[i-lookback:i]
            
            highs = []
            lows = []
            
            for j in range(1, len(window)-1):
                if (window.iloc[j]['high'] > window.iloc[j-1]['high'] and 
                    window.iloc[j]['high'] > window.iloc[j+1]['high']):
                    highs.append((j, window.iloc[j]['high']))
                    
                if (window.iloc[j]['low'] < window.iloc[j-1]['low'] and 
                    window.iloc[j]['low'] < window.iloc[j+1]['low']):
                    lows.append((j, window.iloc[j]['low']))
            
            if len(highs) >= 2 and len(lows) >= 2:
                high_indices = [h[0] for h in highs]
                high_prices = [h[1] for h in highs]
                low_indices = [l[0] for l in lows]
                low_prices = [l[1] for l in lows]
                
                resistance_slope, resistance_intercept = np.polyfit(high_indices, high_prices, 1)
                support_slope, support_intercept = np.polyfit(low_indices, low_prices, 1)
                
                # Both descending, resistance falling faster (converging)
                if resistance_slope < 0 and support_slope < 0 and resistance_slope < support_slope:
                    current_price = self.df.iloc[i]['close']
                    resistance_at_current = resistance_slope * (lookback - 1) + resistance_intercept
                    
                    # Breakout above resistance
                    if current_price > resistance_at_current:
                        signals.append({
                            'index': i,
                            'pattern': 'falling_wedge',
                            'breakout_price': current_price,
                            'direction': 'bullish'
                        })
        
        return signals
    
    # ==================== DOUBLE TOP/BOTTOM ====================
    
    def detect_double_top(self, lookback=30, tolerance=0.01):
        """
        Double Top: Two peaks at similar levels, bearish reversal
        
        Args:
            lookback: Candles to search for pattern
            tolerance: Price similarity tolerance (1%)
        """
        signals = []
        
        for i in range(lookback, len(self.df)):
            window = self.df.iloc[i-lookback:i]
            
            # Find peaks (swing highs)
            peaks = []
            for j in range(2, len(window)-2):
                if (window.iloc[j]['high'] > window.iloc[j-1]['high'] and 
                    window.iloc[j]['high'] > window.iloc[j-2]['high'] and
                    window.iloc[j]['high'] > window.iloc[j+1]['high'] and 
                    window.iloc[j]['high'] > window.iloc[j+2]['high']):
                    peaks.append((i-lookback+j, window.iloc[j]['high']))
            
            # Need at least 2 peaks
            if len(peaks) >= 2:
                # Check last two peaks
                peak1_idx, peak1_price = peaks[-2]
                peak2_idx, peak2_price = peaks[-1]
                
                # Peaks should be similar in price
                if abs(peak1_price - peak2_price) / peak1_price < tolerance:
                    # Find the trough between peaks
                    between_data = self.df.iloc[peak1_idx:peak2_idx]
                    trough_price = between_data['low'].min()
                    
                    current_price = self.df.iloc[i]['close']
                    
                    # Breakout below neckline (trough)
                    if current_price < trough_price:
                        signals.append({
                            'index': i,
                            'pattern': 'double_top',
                            'peak_level': (peak1_price + peak2_price) / 2,
                            'neckline': trough_price,
                            'breakout_price': current_price,
                            'direction': 'bearish'
                        })
        
        return signals
    
    def detect_double_bottom(self, lookback=30, tolerance=0.01):
        """
        Double Bottom: Two troughs at similar levels, bullish reversal
        """
        signals = []
        
        for i in range(lookback, len(self.df)):
            window = self.df.iloc[i-lookback:i]
            
            # Find troughs (swing lows)
            troughs = []
            for j in range(2, len(window)-2):
                if (window.iloc[j]['low'] < window.iloc[j-1]['low'] and 
                    window.iloc[j]['low'] < window.iloc[j-2]['low'] and
                    window.iloc[j]['low'] < window.iloc[j+1]['low'] and 
                    window.iloc[j]['low'] < window.iloc[j+2]['low']):
                    troughs.append((i-lookback+j, window.iloc[j]['low']))
            
            if len(troughs) >= 2:
                trough1_idx, trough1_price = troughs[-2]
                trough2_idx, trough2_price = troughs[-1]
                
                # Troughs should be similar in price
                if abs(trough1_price - trough2_price) / trough1_price < tolerance:
                    # Find the peak between troughs
                    between_data = self.df.iloc[trough1_idx:trough2_idx]
                    peak_price = between_data['high'].max()
                    
                    current_price = self.df.iloc[i]['close']
                    
                    # Breakout above neckline (peak)
                    if current_price > peak_price:
                        signals.append({
                            'index': i,
                            'pattern': 'double_bottom',
                            'trough_level': (trough1_price + trough2_price) / 2,
                            'neckline': peak_price,
                            'breakout_price': current_price,
                            'direction': 'bullish'
                        })
        
        return signals
    
    # ==================== HEAD AND SHOULDERS ====================
    
    def detect_head_and_shoulders(self, lookback=40, tolerance=0.015):
        """
        Head and Shoulders: Three peaks, middle highest
        Strong bearish reversal
        """
        signals = []
        
        for i in range(lookback, len(self.df)):
            window = self.df.iloc[i-lookback:i]
            
            # Find peaks
            peaks = []
            for j in range(2, len(window)-2):
                if (window.iloc[j]['high'] > window.iloc[j-1]['high'] and 
                    window.iloc[j]['high'] > window.iloc[j-2]['high'] and
                    window.iloc[j]['high'] > window.iloc[j+1]['high'] and 
                    window.iloc[j]['high'] > window.iloc[j+2]['high']):
                    peaks.append((i-lookback+j, window.iloc[j]['high']))
            
            # Need exactly 3 peaks for classic H&S
            if len(peaks) >= 3:
                left_shoulder_idx, left_shoulder = peaks[-3]
                head_idx, head = peaks[-2]
                right_shoulder_idx, right_shoulder = peaks[-1]
                
                # Head should be highest
                if head > left_shoulder and head > right_shoulder:
                    # Shoulders should be similar height
                    if abs(left_shoulder - right_shoulder) / left_shoulder < tolerance:
                        # Find neckline (lows between peaks)
                        left_trough = self.df.iloc[left_shoulder_idx:head_idx]['low'].min()
                        right_trough = self.df.iloc[head_idx:right_shoulder_idx]['low'].min()
                        neckline = (left_trough + right_trough) / 2
                        
                        current_price = self.df.iloc[i]['close']
                        
                        # Breakout below neckline
                        if current_price < neckline:
                            signals.append({
                                'index': i,
                                'pattern': 'head_and_shoulders',
                                'head_price': head,
                                'shoulder_price': (left_shoulder + right_shoulder) / 2,
                                'neckline': neckline,
                                'breakout_price': current_price,
                                'direction': 'bearish',
                                'target': neckline - (head - neckline)  # Measured move
                            })
        
        return signals
    
    def detect_inverse_head_and_shoulders(self, lookback=40, tolerance=0.015):
        """
        Inverse Head and Shoulders: Three troughs, middle lowest
        Strong bullish reversal
        """
        signals = []
        
        for i in range(lookback, len(self.df)):
            window = self.df.iloc[i-lookback:i]
            
            # Find troughs
            troughs = []
            for j in range(2, len(window)-2):
                if (window.iloc[j]['low'] < window.iloc[j-1]['low'] and 
                    window.iloc[j]['low'] < window.iloc[j-2]['low'] and
                    window.iloc[j]['low'] < window.iloc[j+1]['low'] and 
                    window.iloc[j]['low'] < window.iloc[j+2]['low']):
                    troughs.append((i-lookback+j, window.iloc[j]['low']))
            
            if len(troughs) >= 3:
                left_shoulder_idx, left_shoulder = troughs[-3]
                head_idx, head = troughs[-2]
                right_shoulder_idx, right_shoulder = troughs[-1]
                
                # Head should be lowest
                if head < left_shoulder and head < right_shoulder:
                    # Shoulders should be similar
                    if abs(left_shoulder - right_shoulder) / left_shoulder < tolerance:
                        # Find neckline (highs between troughs)
                        left_peak = self.df.iloc[left_shoulder_idx:head_idx]['high'].max()
                        right_peak = self.df.iloc[head_idx:right_shoulder_idx]['high'].max()
                        neckline = (left_peak + right_peak) / 2
                        
                        current_price = self.df.iloc[i]['close']
                        
                        # Breakout above neckline
                        if current_price > neckline:
                            signals.append({
                                'index': i,
                                'pattern': 'inverse_head_and_shoulders',
                                'head_price': head,
                                'shoulder_price': (left_shoulder + right_shoulder) / 2,
                                'neckline': neckline,
                                'breakout_price': current_price,
                                'direction': 'bullish',
                                'target': neckline + (neckline - head)  # Measured move
                            })
        
        return signals
    
    # ==================== ROUNDED TOP/BOTTOM ====================
    
    def detect_rounded_top(self, lookback=30):
        """
        Rounded Top: U-shaped price decline
        Bearish reversal
        """
        signals = []
        
        for i in range(lookback, len(self.df)):
            window = self.df.iloc[i-lookback:i]
            
            # Fit a polynomial curve to the highs
            indices = np.arange(len(window))
            highs = window['high'].values
            
            # Use quadratic fit
            try:
                coeffs = np.polyfit(indices, highs, 2)
                
                # Negative quadratic coefficient indicates downward curve
                if coeffs[0] < 0:
                    # Calculate R-squared to measure fit quality
                    fitted_curve = np.polyval(coeffs, indices)
                    residuals = highs - fitted_curve
                    ss_res = np.sum(residuals**2)
                    ss_tot = np.sum((highs - np.mean(highs))**2)
                    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                    
                    # Good curve fit (R² > 0.7) indicates rounded pattern
                    if r_squared > 0.7:
                        current_price = self.df.iloc[i]['close']
                        support_level = window['low'].min()
                        
                        # Breakout below support
                        if current_price < support_level:
                            signals.append({
                                'index': i,
                                'pattern': 'rounded_top',
                                'curve_quality': r_squared,
                                'support_level': support_level,
                                'breakout_price': current_price,
                                'direction': 'bearish'
                            })
            except:
                pass
        
        return signals
    
    def detect_rounded_bottom(self, lookback=30):
        """
        Rounded Bottom: U-shaped price rise
        Bullish reversal
        """
        signals = []
        
        for i in range(lookback, len(self.df)):
            window = self.df.iloc[i-lookback:i]
            
            indices = np.arange(len(window))
            lows = window['low'].values
            
            try:
                coeffs = np.polyfit(indices, lows, 2)
                
                # Positive quadratic coefficient indicates upward curve
                if coeffs[0] > 0:
                    fitted_curve = np.polyval(coeffs, indices)
                    residuals = lows - fitted_curve
                    ss_res = np.sum(residuals**2)
                    ss_tot = np.sum((lows - np.mean(lows))**2)
                    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                    
                    if r_squared > 0.7:
                        current_price = self.df.iloc[i]['close']
                        resistance_level = window['high'].max()
                        
                        # Breakout above resistance
                        if current_price > resistance_level:
                            signals.append({
                                'index': i,
                                'pattern': 'rounded_bottom',
                                'curve_quality': r_squared,
                                'resistance_level': resistance_level,
                                'breakout_price': current_price,
                                'direction': 'bullish'
                            })
            except:
                pass
        
        return signals
    
    # ==================== CUP AND HANDLE ====================
    
    def detect_cup_and_handle(self, lookback=50, handle_size=10):
        """
        Cup and Handle: Rounded bottom + small consolidation
        Bullish continuation pattern
        """
        signals = []
        
        for i in range(lookback + handle_size, len(self.df)):
            # Cup phase
            cup_data = self.df.iloc[i-lookback-handle_size:i-handle_size]
            
            indices = np.arange(len(cup_data))
            lows = cup_data['low'].values
            
            try:
                # Check for U-shaped cup
                coeffs = np.polyfit(indices, lows, 2)
                
                if coeffs[0] > 0:  # Upward curve
                    fitted_curve = np.polyval(coeffs, indices)
                    residuals = lows - fitted_curve
                    ss_res = np.sum(residuals**2)
                    ss_tot = np.sum((lows - np.mean(lows))**2)
                    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                    
                    if r_squared > 0.6:  # Good cup formation
                        # Handle phase (smaller consolidation)
                        handle_data = self.df.iloc[i-handle_size:i]
                        
                        # Handle should be in upper half of cup
                        cup_depth = cup_data['high'].max() - cup_data['low'].min()
                        handle_depth = handle_data['high'].max() - handle_data['low'].min()
                        
                        if handle_depth < cup_depth * 0.5:  # Handle shallower than cup
                            current_price = self.df.iloc[i]['close']
                            resistance = handle_data['high'].max()
                            
                            # Breakout above handle
                            if current_price > resistance:
                                signals.append({
                                    'index': i,
                                    'pattern': 'cup_and_handle',
                                    'cup_depth': cup_depth,
                                    'handle_resistance': resistance,
                                    'breakout_price': current_price,
                                    'direction': 'bullish',
                                    'target': resistance + cup_depth  # Measured move
                                })
            except:
                pass
        
        return signals
    
    # ==================== TREND PATTERNS ====================
    
    def detect_ascending_staircase(self, lookback=20):
        """
        Ascending Staircase: Higher highs and higher lows
        Uptrend identification
        """
        signals = []
        
        for i in range(lookback, len(self.df)):
            window = self.df.iloc[i-lookback:i]
            
            # Find swing highs and lows
            highs = []
            lows = []
            
            for j in range(1, len(window)-1):
                if (window.iloc[j]['high'] >= window.iloc[j-1]['high'] and 
                    window.iloc[j]['high'] >= window.iloc[j+1]['high']):
                    highs.append(window.iloc[j]['high'])
                    
                if (window.iloc[j]['low'] <= window.iloc[j-1]['low'] and 
                    window.iloc[j]['low'] <= window.iloc[j+1]['low']):
                    lows.append(window.iloc[j]['low'])
            
            # Check for higher highs and higher lows
            if len(highs) >= 2 and len(lows) >= 2:
                higher_highs = all(highs[i] > highs[i-1] for i in range(1, len(highs)))
                higher_lows = all(lows[i] > lows[i-1] for i in range(1, len(lows)))
                
                if higher_highs and higher_lows:
                    signals.append({
                        'index': i,
                        'pattern': 'ascending_staircase',
                        'direction': 'bullish',
                        'strength': len(highs) + len(lows)
                    })
        
        return signals
    
    def detect_descending_staircase(self, lookback=20):
        """
        Descending Staircase: Lower highs and lower lows
        Downtrend identification
        """
        signals = []
        
        for i in range(lookback, len(self.df)):
            window = self.df.iloc[i-lookback:i]
            
            highs = []
            lows = []
            
            for j in range(1, len(window)-1):
                if (window.iloc[j]['high'] >= window.iloc[j-1]['high'] and 
                    window.iloc[j]['high'] >= window.iloc[j+1]['high']):
                    highs.append(window.iloc[j]['high'])
                    
                if (window.iloc[j]['low'] <= window.iloc[j-1]['low'] and 
                    window.iloc[j]['low'] <= window.iloc[j+1]['low']):
                    lows.append(window.iloc[j]['low'])
            
            if len(highs) >= 2 and len(lows) >= 2:
                lower_highs = all(highs[i] < highs[i-1] for i in range(1, len(highs)))
                lower_lows = all(lows[i] < lows[i-1] for i in range(1, len(lows)))
                
                if lower_highs and lower_lows:
                    signals.append({
                        'index': i,
                        'pattern': 'descending_staircase',
                        'direction': 'bearish',
                        'strength': len(highs) + len(lows)
                    })
        
        return signals
    
    # ==================== COMPREHENSIVE DETECTION ====================
    
    def detect_all_patterns(self):
        """
        Run all pattern detectors and return consolidated results
        """
        all_patterns = []
        
        print("\n🔍 Detecting All Patterns...")
        print("=" * 60)
        
        # Engulfing patterns
        bullish_eng = self.detect_bullish_engulfing()
        for idx in bullish_eng:
            all_patterns.append({'index': idx, 'pattern': 'bullish_engulfing', 'direction': 'bullish'})
        print(f"✓ Bullish Engulfing: {len(bullish_eng)} signals")
        
        bearish_eng = self.detect_bearish_engulfing()
        for idx in bearish_eng:
            all_patterns.append({'index': idx, 'pattern': 'bearish_engulfing', 'direction': 'bearish'})
        print(f"✓ Bearish Engulfing: {len(bearish_eng)} signals")
        
        # Triangle patterns
        asc_tri = self.detect_ascending_triangle()
        all_patterns.extend(asc_tri)
        print(f"✓ Ascending Triangle: {len(asc_tri)} signals")
        
        desc_tri = self.detect_descending_triangle()
        all_patterns.extend(desc_tri)
        print(f"✓ Descending Triangle: {len(desc_tri)} signals")
        
        sym_tri = self.detect_symmetrical_triangle()
        all_patterns.extend(sym_tri)
        print(f"✓ Symmetrical Triangle: {len(sym_tri)} signals")
        
        # Flag patterns
        bull_flags = self.detect_bull_flag()
        all_patterns.extend(bull_flags)
        print(f"✓ Bull Flag: {len(bull_flags)} signals")
        
        bear_flags = self.detect_bear_flag()
        all_patterns.extend(bear_flags)
        print(f"✓ Bear Flag: {len(bear_flags)} signals")
        
        # Wedge patterns
        rising_wedge = self.detect_rising_wedge()
        all_patterns.extend(rising_wedge)
        print(f"✓ Rising Wedge: {len(rising_wedge)} signals")
        
        falling_wedge = self.detect_falling_wedge()
        all_patterns.extend(falling_wedge)
        print(f"✓ Falling Wedge: {len(falling_wedge)} signals")
        
        # Double patterns
        double_top = self.detect_double_top()
        all_patterns.extend(double_top)
        print(f"✓ Double Top: {len(double_top)} signals")
        
        double_bottom = self.detect_double_bottom()
        all_patterns.extend(double_bottom)
        print(f"✓ Double Bottom: {len(double_bottom)} signals")
        
        # Head and shoulders
        h_and_s = self.detect_head_and_shoulders()
        all_patterns.extend(h_and_s)
        print(f"✓ Head and Shoulders: {len(h_and_s)} signals")
        
        inv_h_and_s = self.detect_inverse_head_and_shoulders()
        all_patterns.extend(inv_h_and_s)
        print(f"✓ Inverse H&S: {len(inv_h_and_s)} signals")
        
        # Rounded patterns
        rounded_top = self.detect_rounded_top()
        all_patterns.extend(rounded_top)
        print(f"✓ Rounded Top: {len(rounded_top)} signals")
        
        rounded_bottom = self.detect_rounded_bottom()
        all_patterns.extend(rounded_bottom)
        print(f"✓ Rounded Bottom: {len(rounded_bottom)} signals")
        
        # Cup and handle
        cup_handle = self.detect_cup_and_handle()
        all_patterns.extend(cup_handle)
        print(f"✓ Cup and Handle: {len(cup_handle)} signals")
        
        # Trend patterns
        asc_stair = self.detect_ascending_staircase()
        all_patterns.extend(asc_stair)
        print(f"✓ Ascending Staircase: {len(asc_stair)} signals")
        
        desc_stair = self.detect_descending_staircase()
        all_patterns.extend(desc_stair)
        print(f"✓ Descending Staircase: {len(desc_stair)} signals")
        
        print("=" * 60)
        print(f"✅ TOTAL PATTERNS DETECTED: {len(all_patterns)}")
        
        return sorted(all_patterns, key=lambda x: x['index'])
    
    # ==================== FILTERED PATTERNS WITH CONTEXT ====================
    
    def get_high_quality_signals(self, pattern_results):
        """
        Filter patterns based on quality criteria:
        - Volume confirmation
        - RSI context
        - Trend alignment
        - S/R confluence
        """
        quality_signals = []
        
        for pattern in pattern_results:
            idx = pattern['index']
            
            if idx >= len(self.df):
                continue
            
            candle = self.df.iloc[idx]
            
            # Skip if missing data
            if pd.isna(candle['rsi']) or pd.isna(candle['volume_ratio']):
                continue
            
            # Volume confirmation
            volume_ok = candle['volume_ratio'] > 1.2  # 20% above average
            
            # RSI context
            if pattern['direction'] == 'bullish':
                rsi_ok = candle['rsi'] < 70  # Not overbought
            else:
                rsi_ok = candle['rsi'] > 30  # Not oversold
            
            # Add quality score
            quality_score = 0
            if volume_ok:
                quality_score += 1
            if rsi_ok:
                quality_score += 1
            
            if quality_score >= 1:  # At least one confirmation
                pattern['quality_score'] = quality_score
                pattern['volume_ratio'] = candle['volume_ratio']
                pattern['rsi'] = candle['rsi']
                quality_signals.append(pattern)
        
        return quality_signals
    
    # ==================== UTILITY METHODS ====================
    
    def get_pattern_details(self, index):
        """Get comprehensive details for a pattern at given index"""
        if index >= len(self.df) or index < 0:
            return None
        
        candle = self.df.iloc[index]
        prev_candle = self.df.iloc[index-1] if index > 0 else None
        
        details = {
            'time': candle['time'],
            'open': candle['open'],
            'high': candle['high'],
            'low': candle['low'],
            'close': candle['close'],
            'volume': candle['volume'],
            'body_size': candle['body'],
            'is_green': candle['close'] > candle['open'],
            'rsi': candle['rsi'],
            'ema_50': candle['ema_50'],
            'volume_ratio': candle['volume_ratio']
        }
        
        if prev_candle is not None:
            details['prev_body_size'] = prev_candle['body']
            details['body_ratio'] = details['body_size'] / prev_candle['body'] if prev_candle['body'] > 0 else 0
        
        return details
    
    def calculate_risk_reward(self, entry, stop_loss, target):
        """Calculate risk-reward ratio"""
        risk = abs(entry - stop_loss)
        reward = abs(target - entry)
        
        if risk == 0:
            return 0
        
        return reward / risk
    
    # ==================== LEGACY S/R INTEGRATION METHODS ====================
    # These methods maintain backward compatibility with existing backtests
    
    def detect_bullish_engulfing_filtered(self, min_body_ratio=1.5):
        """
        Bullish engulfing with quality filters (legacy method)
        """
        raw_signals = self.detect_bullish_engulfing(min_body_ratio)
        filtered_signals = []
        
        for idx in raw_signals:
            if idx >= len(self.df):
                continue
                
            candle = self.df.iloc[idx]
            
            # RSI filter: Look for oversold or neutral
            if pd.isna(candle['rsi']) or candle['rsi'] > 40:
                continue
            
            # Below EMA filter: Price below moving average (potential reversal)
            if pd.isna(candle['ema_50']) or candle['close'] > candle['ema_50']:
                continue
            
            # Volume confirmation
            if pd.isna(candle['volume_ratio']) or candle['volume_ratio'] < 1.0:
                continue
            
            filtered_signals.append(idx)
        
        return filtered_signals
    
    def detect_bearish_engulfing_filtered(self, min_body_ratio=1.5):
        """
        Bearish engulfing with quality filters (legacy method)
        """
        raw_signals = self.detect_bearish_engulfing(min_body_ratio)
        filtered_signals = []
        
        for idx in raw_signals:
            if idx >= len(self.df):
                continue
                
            candle = self.df.iloc[idx]
            
            # RSI filter: Look for overbought or neutral
            if pd.isna(candle['rsi']) or candle['rsi'] < 60:
                continue
            
            # Above EMA filter: Price above moving average (potential reversal)
            if pd.isna(candle['ema_50']) or candle['close'] < candle['ema_50']:
                continue
            
            # Volume confirmation
            if pd.isna(candle['volume_ratio']) or candle['volume_ratio'] < 1.0:
                continue
            
            filtered_signals.append(idx)
        
        return filtered_signals
    
    def detect_bullish_engulfing_with_SR(self, min_body_ratio=1.5):
        """
        Bullish engulfing that appears AT SUPPORT
        
        Returns:
            List of dicts with pattern details and S/R levels
        """
        try:
            from support_resistance import SupportResistanceDetector
        except ImportError:
            print("⚠️  Warning: support_resistance module not found. Returning filtered signals without S/R.")
            filtered = self.detect_bullish_engulfing_filtered(min_body_ratio)
            return [{'index': idx, 'price': self.df.iloc[idx]['close']} for idx in filtered]
        
        filtered_signals = self.detect_bullish_engulfing_filtered(min_body_ratio)
        
        sr_detector = SupportResistanceDetector(self.df, lookback_candles=150)
        
        sr_confirmed = []
        
        for idx in filtered_signals:
            if idx >= len(self.df):
                continue
                
            candle = self.df.iloc[idx]
            price = candle['close']
            
            try:
                at_support, support_info = sr_detector.is_at_support(price, tolerance_pct=0.3)
                
                if at_support and support_info and support_info.get('strength', 0) >= 2:
                    sr_confirmed.append({
                        'index': idx,
                        'price': price,
                        'support_level': support_info['price'],
                        'support_strength': support_info['strength']
                    })
            except Exception as e:
                # If S/R check fails, still include the signal without S/R data
                sr_confirmed.append({
                    'index': idx,
                    'price': price,
                    'support_level': None,
                    'support_strength': 0
                })
        
        return sr_confirmed
    
    def detect_bearish_engulfing_with_SR(self, min_body_ratio=1.5):
        """
        Bearish engulfing that appears AT RESISTANCE
        
        Returns:
            List of dicts with pattern details and S/R levels
        """
        try:
            from support_resistance import SupportResistanceDetector
        except ImportError:
            print("⚠️  Warning: support_resistance module not found. Returning filtered signals without S/R.")
            filtered = self.detect_bearish_engulfing_filtered(min_body_ratio)
            return [{'index': idx, 'price': self.df.iloc[idx]['close']} for idx in filtered]
        
        filtered_signals = self.detect_bearish_engulfing_filtered(min_body_ratio)
        
        sr_detector = SupportResistanceDetector(self.df, lookback_candles=150)
        sr_confirmed = []
        
        for idx in filtered_signals:
            if idx >= len(self.df):
                continue
                
            candle = self.df.iloc[idx]
            price = candle['close']
            
            try:
                at_resistance, resistance_info = sr_detector.is_at_resistance(price, tolerance_pct=0.3)
                
                if at_resistance and resistance_info and resistance_info.get('strength', 0) >= 2:
                    sr_confirmed.append({
                        'index': idx,
                        'price': price,
                        'resistance_level': resistance_info['price'],
                        'resistance_strength': resistance_info['strength']
                    })
            except Exception as e:
                # If S/R check fails, still include the signal without S/R data
                sr_confirmed.append({
                    'index': idx,
                    'price': price,
                    'resistance_level': None,
                    'resistance_strength': 0
                })
        
        return sr_confirmed
                                