# Complete Testing Guide - Days 1-7

## Prerequisites Checklist
- [ ] MT5 installed and running
- [ ] Demo account created and logged in
- [ ] XAUUSD symbol enabled in Market Watch
- [ ] Virtual environment activated (`venv\Scripts\activate`)
- [ ] All packages installed (`pip install -r requirements.txt`)

---

## DAY 1-2: Foundation Tests

### Test 1: Basic MT5 Connection
```powershell
python data_fetcher.py
```

**Expected Output:**
- MT5 version displayed
- XAUUSD symbol info (bid, ask, spread)
- 200 candles fetched
- CSV file created in `logs/gold_data_test.csv`

**If it fails:**
- Ensure MT5 is running
- Check XAUUSD is enabled in Market Watch
- Verify demo account is logged in

---

### Test 2: MarketDataFetcher Class
```powershell
python test_market_data.py
```

**Expected Output:**
- Connection successful message
- 15-minute data displayed (last 5 candles)
- 1-hour data displayed (last 5 candles)
- Current bid/ask/spread shown
- Clean disconnect

**Success Criteria:** No errors, data looks reasonable

---

### Test 3: Chart Visualization
```powershell
python test_visualizer.py
```

**Expected Output:**
- Chart saved to `logs/gold_chart.png`
- Open the image - should show 100 candlesticks
- Green candles (up) and red candles (down)

**Success Criteria:** Chart is readable and accurate

---

## DAY 3-4: Pattern Detection Tests

### Test 4: Pattern Detection
```powershell
python test_pattern_detector.py
```

**Expected Output:**
- Technical indicators calculated
- Found X bullish engulfing patterns
- Found Y bearish engulfing patterns
- Each pattern shows: index, time, price, body ratio

**Success Criteria:** 
- Finds 5-15 patterns in 500 candles
- Body ratios are > 1.5

---

### Test 5: Visual Pattern Validation
```powershell
python test_visual_validation.py
```

**Expected Output:**
- Chart saved to `logs/patterns_marked.png`
- Green triangles (▲) mark bullish patterns
- Red triangles (▼) mark bearish patterns

**Manual Validation:**
- Open the image
- Look at each marked pattern
- Verify it's actually an engulfing candle
- 80%+ should be correct

---

### Test 6: Quality Filters
```powershell
python test_filters.py
```

**Expected Output:**
```
Bullish engulfing (raw): 12
Bullish engulfing (filtered): 3
Filter reduced signals by 75.0%
```

**Success Criteria:** 
- Filters reduce signals by 60-80%
- At least 2-3 filtered signals remain

---

## DAY 5: Support/Resistance Tests

### Test 7: S/R Detection
```powershell
python test_support_resistance.py
```

**Expected Output:**
- Found 3-7 support levels
- Found 3-7 resistance levels
- Each level shows: price, touches, strength
- Current price checked against levels

**Success Criteria:**
- Levels are spread across price range
- Strength values are 2+
- At least one level near current price

---

### Test 8: S/R + Pattern Integration
```powershell
python test_sr_integration.py
```

**Expected Output:**
```
Signal Funnel:
  Raw patterns: 15
  After filters: 5 (33%)
  After S/R check: 2 (13%)

High-quality signals (with S/R):
  Index 234: Price 2645.30 at support 2645.20 (strength 3)
```

**Success Criteria:**
- S/R filter reduces signals by 50-70%
- Final signals are 10-20% of raw signals
- This is GOOD - quality over quantity

---

## DAY 6: Backtesting Tests

### Test 9: Full Backtest
```powershell
python run_backtest.py
```

**Expected Output:**
```
Loaded 2000 candles from [date] to [date]
Found X high-quality bullish engulfing setups
Simulating trades...
  Trade 1: take_profit | P&L: $45.80
  Trade 2: stop_loss | P&L: -$22.50
  ...

==================================================
BACKTEST RESULTS
==================================================
Initial Capital:    $10,000.00
Final Capital:      $10,XXX.XX
Net Profit:         $XXX.XX (X.XX%)

Total Trades:       X
Winning Trades:     X
Losing Trades:      X
Win Rate:           XX.XX%

Profit Factor:      X.XX
Max Drawdown:       X.XX%
==================================================
```

**Success Criteria:**
- Win rate > 60%
- Profit factor > 1.5
- Max drawdown < 10%
- Net profit > 0%
- Trade log saved to CSV

---

### Test 10: Parameter Optimization
```powershell
python optimize_parameters.py
```

**Expected Duration:** 2-3 minutes

**Expected Output:**
```
Testing parameter combinations...
Optimization complete!

Top 10 Parameter Combinations:
 body_ratio  rr_ratio  risk_pct  total_trades  win_rate  profit_factor  net_profit_pct  max_drawdown
       1.5       2.0       1.0             8     75.00           4.51            2.07          1.12
       ...
```

**Success Criteria:**
- Top combination has profit factor > 2.0
- Win rate > 65%
- Results saved to CSV

---

### Test 11: Performance Analysis
```powershell
python analyze_backtest.py
```

**Expected Output:**
- `logs/equity_curve.png` created
- `logs/trade_analysis.png` created
- Summary statistics printed

**Manual Review:**
- Equity curve should trend upward
- Most exits should be "take_profit" (green)
- Win distribution should be wider than loss distribution

---

## DAY 7: Live Scanner Tests

### Test 12: Live Scanner (Alert Mode)
```powershell
python test_live_scanner.py
```

**Expected Output:**
```
==============================================================
LIVE SCANNER STARTED
Timeframe:      15 minutes
Scan interval:  60 seconds
Auto-trading:   DISABLED
==============================================================

[2025-01-11 16:45:32] Scanning...
✓ Connected to MT5, XAUUSD ready
✓ Fetched 300 candles (15min timeframe)
New candle detected at 2025-01-11 16:45:00
✓ Technical indicators calculated
No high-quality pattern on latest candle

[2025-01-11 16:46:32] Scanning...
No new candle yet, waiting...
...
```

**Let it run for 5-10 minutes, then press Ctrl+C**

**Success Criteria:**
- Scans every 60 seconds
- Detects new candles
- No errors or crashes
- If a pattern appears, shows full trade setup

---

### Test 13: Production Bot (Alert Mode)
```powershell
python production_bot.py
```

**Same as Test 12, but with command-line interface**

**Try different settings:**
```powershell
# 5-minute timeframe
python production_bot.py --timeframe 5 --interval 30

# 1-hour timeframe
python production_bot.py --timeframe 60
```

---

## CRITICAL: Auto-Trading Test (DEMO ONLY)

### Test 14: Auto-Execution (DEMO ACCOUNT REQUIRED)
```powershell
python production_bot.py --auto
```

**WARNING:**
- Only run on DEMO account
- Will execute real orders
- Monitor MT5 terminal for trades

**Expected Behavior:**
- When pattern detected, automatically places order
- Sets SL and TP
- Shows order ticket number
- Trade appears in MT5 terminal

**DO NOT run with --auto on live account until:**
- 30+ days of demo trading
- Verified 60%+ win rate
- Comfortable with system behavior

---

## Troubleshooting

### "MT5 initialization failed"
- MT5 not running → Launch MT5
- Not logged in → Login to demo account
- Wrong account type → Use demo, not live

### "Failed to select XAUUSD"
- Symbol not enabled → Right-click Market Watch → Symbols → Enable XAUUSD
- Wrong broker → Some brokers use "GOLD" instead of "XAUUSD"

### "No data received from MT5"
- Market closed → Wait for market hours (Sunday 5pm - Friday 5pm EST)
- No internet → Check connection
- Symbol suspended → Try different symbol

### "Technical indicators calculated" but no patterns found
- Normal if market is ranging
- Try larger dataset (increase num_candles)
- Filters are working correctly (quality over quantity)

### Backtest shows 0 trades
- Filters too strict → Reduce RSI threshold or body_ratio
- Not enough data → Increase to 3000+ candles
- No S/R levels found → Check support_resistance.py

### Live scanner not detecting patterns
- Patterns are rare (1-2 per day is normal)
- All filters must pass (RSI + EMA + Volume + S/R)
- This is GOOD - quality signals only

---

## Success Metrics

### After completing all tests, you should have:

**Files Created:**
- `logs/gold_data_test.csv`
- `logs/gold_chart.png`
- `logs/patterns_marked.png`
- `logs/backtest_trades.csv`
- `logs/optimization_results.csv`
- `logs/equity_curve.png`
- `logs/trade_analysis.png`
- `logs/signals.txt`

**Performance Targets:**
- Win rate: 60-75%
- Profit factor: 2.0-5.0
- Max drawdown: < 10%
- Signals per day: 1-3 (quality over quantity)

**System Capabilities:**
- ✅ Fetch live data from MT5
- ✅ Detect engulfing patterns
- ✅ Apply multi-layer filters
- ✅ Confirm with S/R levels
- ✅ Backtest on historical data
- ✅ Optimize parameters
- ✅ Scan market in real-time
- ✅ Execute trades automatically (demo)

---

## Next Steps After Testing

1. **Run demo for 30 days**
   - Let scanner run daily
   - Track all signals
   - Verify win rate holds

2. **Paper trade manually**
   - Take signals but don't auto-execute
   - Build confidence in system
   - Learn market behavior

3. **Start small on live**
   - $500-$1000 initial capital
   - 0.5% risk per trade
   - Monitor closely for 2 weeks

4. **Scale gradually**
   - Increase risk to 1% after 20 winning trades
   - Add capital monthly
   - Never risk more than 2% per trade

---

## You're Ready When:

- [ ] All 14 tests pass without errors
- [ ] Backtest shows 60%+ win rate
- [ ] Profit factor > 2.0
- [ ] Understand every line of code
- [ ] Can explain why each filter exists
- [ ] Comfortable with risk management
- [ ] Have 30+ days of demo results
- [ ] Emotionally prepared for losses

**DO NOT skip to live trading. Demo first. Always.**
