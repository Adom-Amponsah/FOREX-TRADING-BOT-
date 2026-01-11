import time
from datetime import datetime
from market_data import MarketDataFetcher
from pattern_detector import PatternDetector

class LiveScanner:
    """Continuously scans for trading patterns"""
    
    def __init__(self, timeframe_min=15, scan_interval_sec=60, auto_trade=False):
        """
        Args:
            timeframe_min: Timeframe to scan (15 min recommended)
            scan_interval_sec: How often to check for new candles
            auto_trade: Enable automatic trade execution (DEMO ONLY)
        """
        self.timeframe_min = timeframe_min
        self.scan_interval_sec = scan_interval_sec
        self.fetcher = MarketDataFetcher()
        self.last_candle_time = None
        
        self.auto_trade = auto_trade
        if auto_trade:
            from order_executor import OrderExecutor
            self.executor = OrderExecutor()
            self.executor.connect()
        
    def scan_once(self):
        """Perform one scan"""
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Scanning...")
        
        self.fetcher.connect()
        df = self.fetcher.get_candles(timeframe_minutes=self.timeframe_min, num_candles=300)
        current_price_info = self.fetcher.get_current_price()
        self.fetcher.disconnect()
        
        latest_candle_time = df.iloc[-1]['time']
        
        if self.last_candle_time and latest_candle_time == self.last_candle_time:
            print("  No new candle yet, waiting...")
            return None
        
        self.last_candle_time = latest_candle_time
        print(f"  New candle detected at {latest_candle_time}")
        
        detector = PatternDetector(df)
        
        bullish_signals = detector.detect_bullish_engulfing_with_SR(min_body_ratio=1.5)
        bearish_signals = detector.detect_bearish_engulfing_with_SR(min_body_ratio=1.5)
        
        latest_idx = len(df) - 1
        
        signal_found = None
        
        for signal in bullish_signals:
            if signal['index'] == latest_idx:
                signal_found = {
                    'type': 'BULLISH ENGULFING',
                    'direction': 'LONG',
                    'price': signal['price'],
                    'support_level': signal['support_level'],
                    'support_strength': signal['support_strength']
                }
                break
        
        for signal in bearish_signals:
            if signal['index'] == latest_idx:
                signal_found = {
                    'type': 'BEARISH ENGULFING',
                    'direction': 'SHORT',
                    'price': signal['price'],
                    'resistance_level': signal['resistance_level'],
                    'resistance_strength': signal['resistance_strength']
                }
                break
        
        if signal_found:
            self._alert_signal(signal_found, df.iloc[-1])
            return signal_found
        else:
            print("  No high-quality pattern on latest candle")
            return None
    
    def _alert_signal(self, signal, candle):
        """Alert when signal detected"""
        print("\n" + "="*60)
        print("🚨 TRADING SIGNAL DETECTED 🚨")
        print("="*60)
        print(f"Pattern:    {signal['type']}")
        print(f"Direction:  {signal['direction']}")
        print(f"Time:       {candle['time']}")
        print(f"Price:      {signal['price']:.2f}")
        
        if signal['direction'] == 'LONG':
            entry = candle['close']
            stop = candle['low'] - 2
            target = entry + (entry - stop) * 2
            print(f"\nTrade Setup:")
            print(f"  Entry:      {entry:.2f}")
            print(f"  Stop Loss:  {stop:.2f}")
            print(f"  Target:     {target:.2f}")
            print(f"  Risk:       {entry - stop:.2f} pips")
            print(f"  Reward:     {target - entry:.2f} pips")
            print(f"  R:R Ratio:  2.0:1")
            print(f"\nSupport Level: {signal['support_level']:.2f} (Strength: {signal['support_strength']})")
            
            if self.auto_trade:
                print("\n🤖 Auto-trading ENABLED - Executing trade...")
                self.executor.execute_trade(
                    direction='long',
                    entry_price=entry,
                    stop_loss=stop,
                    take_profit=target,
                    lot_size=0.01
                )
        
        else:
            entry = candle['close']
            stop = candle['high'] + 2
            target = entry - (stop - entry) * 2
            print(f"\nTrade Setup:")
            print(f"  Entry:      {entry:.2f}")
            print(f"  Stop Loss:  {stop:.2f}")
            print(f"  Target:     {target:.2f}")
            print(f"  Risk:       {stop - entry:.2f} pips")
            print(f"  Reward:     {entry - target:.2f} pips")
            print(f"  R:R Ratio:  2.0:1")
            print(f"\nResistance Level: {signal['resistance_level']:.2f} (Strength: {signal['resistance_strength']})")
            
            if self.auto_trade:
                print("\n🤖 Auto-trading ENABLED - Executing trade...")
                self.executor.execute_trade(
                    direction='short',
                    entry_price=entry,
                    stop_loss=stop,
                    take_profit=target,
                    lot_size=0.01
                )
        
        print("="*60)
        
        with open('logs/signals.txt', 'a') as f:
            f.write(f"\n{datetime.now()} - {signal['type']} at {signal['price']:.2f}\n")
    
    def run(self):
        """Run continuous scanner"""
        print("="*60)
        print("LIVE SCANNER STARTED")
        print("="*60)
        print(f"Timeframe:      {self.timeframe_min} minutes")
        print(f"Scan interval:  {self.scan_interval_sec} seconds")
        print(f"Auto-trading:   {'ENABLED' if self.auto_trade else 'DISABLED'}")
        print(f"Signals logged to: logs/signals.txt")
        print("="*60)
        print("\nPress Ctrl+C to stop\n")
        
        try:
            while True:
                self.scan_once()
                time.sleep(self.scan_interval_sec)
                
        except KeyboardInterrupt:
            print("\n\nScanner stopped by user")
            if self.auto_trade:
                self.executor.disconnect()
