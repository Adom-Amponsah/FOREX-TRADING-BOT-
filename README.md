# Gold Trading Bot - Complete Week 1 System

## Project Structure
```
gold_trading_bot/
├── logs/                          # Output files (charts, data, signals)
│
├── Core Modules:
├── data_fetcher.py               # Initial MT5 connection test
├── market_data.py                # Reusable data fetching class
├── visualizer.py                 # Chart visualization
├── pattern_detector.py           # Pattern detection + filters + S/R
├── multi_timeframe.py            # Multi-timeframe analysis
├── support_resistance.py         # Support/Resistance detection
├── backtest_engine.py            # Backtesting system
├── live_scanner.py               # Real-time pattern scanner
├── order_executor.py             # Trade execution (demo)
│
├── Test Scripts:
├── test_market_data.py           # Test data fetching
├── test_visualizer.py            # Test chart generation
├── test_pattern_detector.py      # Test pattern detection
├── test_visual_validation.py     # Test pattern visualization
├── test_filters.py               # Test quality filters
├── test_support_resistance.py    # Test S/R detection
├── test_sr_integration.py        # Test S/R + patterns
├── test_live_scanner.py          # Test live scanner
│
├── Production Scripts:
├── run_backtest.py               # Run full backtest
├── optimize_parameters.py        # Parameter optimization
├── analyze_backtest.py           # Generate performance charts
├── production_bot.py             # Production scanner with CLI
│
└── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Setup Instructions

### 1. Install MetaTrader 5
- Download from: https://www.metatrader5.com/en/download
- Open demo account with MetaQuotes Software Corp
- Enable XAUUSD symbol in Market Watch

### 2. Python Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Test Connection
```powershell
python data_fetcher.py
```

## Complete Testing Sequence

### Days 1-4: Foundation Tests
```powershell
# Test 1: Data fetching
python test_market_data.py

# Test 2: Chart visualization
python test_visualizer.py

# Test 3: Pattern detection
python test_pattern_detector.py

# Test 4: Visual validation
python test_visual_validation.py

# Test 5: Quality filters
python test_filters.py
```

### Days 5-7: Advanced Tests
```powershell
# Test 6: Support/Resistance detection
python test_support_resistance.py

# Test 7: S/R + Pattern integration
python test_sr_integration.py

# Test 8: Run full backtest
python run_backtest.py

# Test 9: Parameter optimization (takes 2-3 minutes)
python optimize_parameters.py

# Test 10: Generate performance charts
python analyze_backtest.py

# Test 11: Live scanner (alert-only mode)
python test_live_scanner.py
# Press Ctrl+C to stop
```

## Key Features

### MarketDataFetcher
- Connects to MT5
- Fetches multiple timeframes (1m, 5m, 15m, 30m, 1h, 4h, D1)
- Returns clean pandas DataFrames
- Gets current bid/ask prices

### PatternDetector
- Detects bullish/bearish engulfing patterns
- Calculates technical indicators (RSI, EMA, ATR, Volume MA)
- Applies quality filters (RSI, trend, volume)
- Integrates support/resistance confirmation
- Returns high-probability setups only

### SupportResistanceDetector
- Identifies swing highs and lows
- Clusters price levels into zones
- Calculates zone strength (number of touches)
- Validates patterns at key levels

### BacktestEngine
- Simulates trades on historical data
- Dynamic position sizing based on risk
- Tracks stop loss and take profit hits
- Calculates comprehensive performance metrics:
  - Win rate
  - Profit factor
  - Max drawdown
  - Average win/loss
  - Equity curve

### LiveScanner
- Continuously monitors market for patterns
- Detects new candle formation
- Applies all filters in real-time
- Alerts with complete trade setup
- Optional auto-execution (demo only)

### OrderExecutor
- Executes market orders via MT5
- Sets stop loss and take profit automatically
- Tracks orders with magic number
- Demo account compatible

### ChartVisualizer
- Creates candlestick charts
- Marks patterns with green/red triangles
- Generates equity curves
- P&L distribution analysis
- Exit reason pie charts

## Production Deployment

### Alert-Only Mode (Safe)
```powershell
python production_bot.py
```

### Auto-Trading Mode (DEMO ACCOUNT ONLY)
```powershell
python production_bot.py --auto
```

### Custom Settings
```powershell
# 5-minute timeframe, scan every 30 seconds
python production_bot.py --timeframe 5 --interval 30

# 1-hour timeframe with auto-trading
python production_bot.py --timeframe 60 --auto
```

## Important Notes
- MT5 must be running for data fetching
- Demo account is free and unlimited
- All times are in MT5 server time
- Spread varies with market conditions
