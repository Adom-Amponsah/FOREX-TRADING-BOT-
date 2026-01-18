import time
from datetime import datetime
import os
import urllib.parse
import urllib.request
from market_data import MarketDataFetcher
from pattern_detector import PatternDetector


def _safe_float(v, default=0.0) -> float:
    try:
        if v is None:
            return float(default)
        return float(v)
    except Exception:
        return float(default)


def _send_telegram_message(text: str) -> bool:
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if not token or not chat_id:
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True,
    }

    data = urllib.parse.urlencode(payload).encode('utf-8')
    try:
        req = urllib.request.Request(url, data=data, method='POST')
        with urllib.request.urlopen(req, timeout=15) as resp:
            return 200 <= int(resp.status) < 300
    except Exception:
        return False

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

        self.min_confidence = 75
        self.auto_trade_min_confidence = 85
        self.max_spread = 50
        self.sr_min_strength = 2
        
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

        df = detector.df

        falling_wedge_signals = detector.detect_falling_wedge(lookback=20)

        latest_idx = len(df) - 1
        
        signal_found = None

        for signal in falling_wedge_signals:
            if signal.get('index') == latest_idx:
                candle = df.iloc[latest_idx]
                confidence, context = self._score_falling_wedge(candle=candle, price_info=current_price_info, df=df)
                signal_found = {
                    'type': 'FALLING_WEDGE',
                    'direction': 'LONG',
                    'price': float(candle['close']),
                    'confidence': confidence,
                    'context': context,
                }
                break
        
        if signal_found:
            if signal_found.get('confidence', 0) >= self.min_confidence:
                self._alert_signal(signal_found, df.iloc[-1], price_info=current_price_info)
                return signal_found
            else:
                print(f"  Signal found but confidence too low ({signal_found.get('confidence', 0):.1f} < {self.min_confidence})")
                return None
            return signal_found
        else:
            print("  No high-quality pattern on latest candle")
            return None

    def _score_falling_wedge(self, candle, price_info, df):
        """Return (confidence_score, context_dict)"""
        confidence = 60.0

        spread = _safe_float(price_info.get('spread')) if price_info else 0.0
        if spread > self.max_spread:
            confidence -= 25

        rsi = _safe_float(candle['rsi']) if 'rsi' in candle.index else 0.0
        ema20 = _safe_float(candle['ema_20']) if 'ema_20' in candle.index else 0.0
        ema50 = _safe_float(candle['ema_50']) if 'ema_50' in candle.index else 0.0
        atr = _safe_float(candle['atr']) if 'atr' in candle.index else 0.0
        vol_ratio = _safe_float(candle['volume_ratio']) if 'volume_ratio' in candle.index else 0.0

        trend_ok = (ema20 > ema50) if (ema20 and ema50) else False
        if trend_ok:
            confidence += 10
        else:
            confidence -= 10

        if rsi and rsi < 65:
            confidence += 5
        elif rsi and rsi > 70:
            confidence -= 5

        if vol_ratio and vol_ratio >= 1.2:
            confidence += 5

        sr_at_support = False
        sr_strength = 0
        sr_level = None
        try:
            from support_resistance import SupportResistanceDetector
            sr_detector = SupportResistanceDetector(df, lookback_candles=150)
            sr_at_support, sr_info = sr_detector.is_at_support(float(candle['close']), tolerance_pct=0.3)
            if sr_info:
                sr_strength = int(sr_info.get('strength', 0))
                sr_level = float(sr_info.get('price'))
            if sr_at_support and sr_strength >= self.sr_min_strength:
                confidence += 10
        except Exception:
            pass

        h1_trend = None
        h4_trend = None
        try:
            from multi_timeframe import MultiTimeframeAnalyzer
            mtf = MultiTimeframeAnalyzer()
            h1_trend = mtf.check_higher_timeframe_trend(candle['time'], timeframe_min=60)
            h4_trend = mtf.check_higher_timeframe_trend(candle['time'], timeframe_min=240)
            if h1_trend == 'uptrend':
                confidence += 7
            elif h1_trend == 'downtrend':
                confidence -= 7
            if h4_trend == 'uptrend':
                confidence += 8
            elif h4_trend == 'downtrend':
                confidence -= 8
        except Exception:
            pass

        confidence = max(0.0, min(100.0, confidence))

        context = {
            'spread': spread,
            'rsi': rsi,
            'ema20': ema20,
            'ema50': ema50,
            'atr': atr,
            'volume_ratio': vol_ratio,
            'sr_at_support': sr_at_support,
            'sr_strength': sr_strength,
            'sr_level': sr_level,
            'h1_trend': h1_trend,
            'h4_trend': h4_trend,
        }

        return confidence, context
    
    def _alert_signal(self, signal, candle, price_info=None):
        """Alert when signal detected"""
        print("\n" + "="*60)
        print("🚨 TRADING SIGNAL DETECTED 🚨")
        print("="*60)
        print(f"Pattern:    {signal['type']}")
        print(f"Direction:  {signal['direction']}")
        print(f"Time:       {candle['time']}")
        print(f"Price:      {signal['price']:.2f}")
        if 'confidence' in signal:
            print(f"Confidence: {signal['confidence']:.1f}/100")
        if price_info and 'spread' in price_info:
            print(f"Spread:     {price_info['spread']}")
        if 'context' in signal and signal['context']:
            ctx = signal['context']
            if ctx.get('h1_trend') or ctx.get('h4_trend'):
                print(f"Trend:      H1={ctx.get('h1_trend')} | H4={ctx.get('h4_trend')}")
            if ctx.get('sr_level') is not None:
                print(f"Support:    {ctx.get('sr_level'):.2f} (Strength: {ctx.get('sr_strength', 0)})")
        
        if signal['direction'] == 'LONG':
            entry = candle['close']
            atr = _safe_float(candle['atr']) if 'atr' in candle.index else 0.0
            stop = candle['low'] - (atr * 0.5 if atr else 2)
            target = entry + (entry - stop) * 2
            print(f"\nTrade Setup:")
            print(f"  Entry:      {entry:.2f}")
            print(f"  Stop Loss:  {stop:.2f}")
            print(f"  Target:     {target:.2f}")
            print(f"  Risk:       {entry - stop:.2f} pips")
            print(f"  Reward:     {target - entry:.2f} pips")
            print(f"  R:R Ratio:  2.0:1")

            msg_lines = []
            msg_lines.append("<b>🚨 TRADE ALERT</b>")
            msg_lines.append(f"<b>Pattern:</b> {signal.get('type')}")
            msg_lines.append(f"<b>Direction:</b> {signal.get('direction')}")
            msg_lines.append(f"<b>Time:</b> {candle['time']}")
            msg_lines.append(f"<b>Price:</b> {float(signal.get('price', entry)):.2f}")
            msg_lines.append(f"<b>Confidence:</b> {float(signal.get('confidence', 0.0)):.1f}/100")

            if price_info and 'spread' in price_info:
                msg_lines.append(f"<b>Spread:</b> {price_info.get('spread')}")

            if 'context' in signal and signal['context']:
                ctx = signal['context']
                if ctx.get('h1_trend') or ctx.get('h4_trend'):
                    msg_lines.append(f"<b>Trend:</b> H1={ctx.get('h1_trend')} | H4={ctx.get('h4_trend')}")
                if ctx.get('sr_level') is not None:
                    msg_lines.append(f"<b>Support:</b> {ctx.get('sr_level'):.2f} (Strength: {ctx.get('sr_strength', 0)})")
                if ctx.get('rsi'):
                    msg_lines.append(f"<b>RSI:</b> {ctx.get('rsi'):.1f}")
                if ctx.get('volume_ratio'):
                    msg_lines.append(f"<b>Vol ratio:</b> {ctx.get('volume_ratio'):.2f}")

            msg_lines.append("")
            msg_lines.append("<b>Setup</b>")
            msg_lines.append(f"Entry: {entry:.2f}")
            msg_lines.append(f"SL: {stop:.2f}")
            msg_lines.append(f"TP: {target:.2f}")
            msg_lines.append("RR: 2.0")

            sent = _send_telegram_message("\n".join(msg_lines))
            if sent:
                print("✓ Telegram alert sent")
            else:
                if os.getenv('TELEGRAM_BOT_TOKEN') and os.getenv('TELEGRAM_CHAT_ID'):
                    print("⚠️  Telegram alert failed to send")
            
            if self.auto_trade:
                can_trade = True
                if signal.get('confidence', 0) < self.auto_trade_min_confidence:
                    can_trade = False
                    print(f"\n🤖 Auto-trading SKIPPED - confidence below {self.auto_trade_min_confidence}")
                if price_info and _safe_float(price_info.get('spread')) > self.max_spread:
                    can_trade = False
                    print(f"\n🤖 Auto-trading SKIPPED - spread above {self.max_spread}")
                if can_trade:
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
            atr = _safe_float(candle['atr']) if 'atr' in candle.index else 0.0
            stop = candle['high'] + (atr * 0.5 if atr else 2)
            target = entry - (stop - entry) * 2
            print(f"\nTrade Setup:")
            print(f"  Entry:      {entry:.2f}")
            print(f"  Stop Loss:  {stop:.2f}")
            print(f"  Target:     {target:.2f}")
            print(f"  Risk:       {stop - entry:.2f} pips")
            print(f"  Reward:     {entry - target:.2f} pips")
            print(f"  R:R Ratio:  2.0:1")
            if self.auto_trade:
                print("\n🤖 Auto-trading SKIPPED - short direction not enabled for this strategy")
        
        print("="*60)
        
        with open('logs/signals.txt', 'a') as f:
            conf = signal.get('confidence', 0.0)
            f.write(f"\n{datetime.now()} - {signal['type']} {signal.get('direction')} at {signal['price']:.2f} | conf={conf:.1f}\n")
    
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
