# Forex Trading Bot - Production System

## Project Structure
```
forex_trading_bot/
├── logs/                          # Output files (charts, data, signals)
│
├── Core Modules:
├── data_fetcher.py               # Initial MT5 connection test
├── market_data.py                # Reusable data fetching class
├── visualizer.py                 # Chart visualization
├── pattern_detector.py           # Pattern detection + filters + S/R (11 patterns)
├── multi_timeframe.py            # Multi-timeframe analysis
├── support_resistance.py         # Support/Resistance detection
├── backtest_engine.py            # Backtesting system
├── live_scanner.py               # Real-time pattern scanner with Telegram alerts
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
├── comprehensive_backtest.py     # Comprehensive backtest for all 11 patterns
├── production_bot.py             # Production scanner with CLI and Telegram alerts
│
├── Configuration:
├── .env                          # Environment variables (Telegram bot token/chat ID)
└── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Setup Instructions

### 1. Install MetaTrader 5
- Download from: https://www.metatrader5.com/en/download
- Open demo account with MetaQuotes Software Corp
- Enable XAUUSD symbol in Market Watch

### 2. Python Environment (Python 3.10)
```powershell
# Create virtual environment with Python 3.10
py -3.10 -m venv .venv

# Activate it
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Telegram Alerts (Optional)
Create a `.env` file with your Telegram bot credentials:
```powershell
# Set environment variables
$env:TELEGRAM_BOT_TOKEN="your_bot_token_here"
$env:TELEGRAM_CHAT_ID="your_chat_id_here"
```

### 4. Test Connection
```powershell
python data_fetcher.py
```

## Production Usage

### Comprehensive Backtesting
```powershell
# Run comprehensive backtest on all 11 patterns
python comprehensive_backtest.py
```
This will:
- Test all 11 patterns on 2000 candles of historical data
- Apply high-precision filters (trend, RSI, ATR)
- Generate performance statistics for each pattern
- Save trade logs to `logs/backtest_*.csv`
- Export ML dataset to `logs/ml_dataset.csv`

### Production Trading Bot

#### Alert-Only Mode (Recommended)
```powershell
# Default: 15-minute timeframe, scan every 60 seconds
python production_bot.py --timeframe 15 --interval 60

# Custom timeframe and interval
python production_bot.py --timeframe 5 --interval 30
python production_bot.py --timeframe 60 --interval 120
```

#### Auto-Trading Mode (DEMO ACCOUNT ONLY)
```powershell
# Enable automatic trade execution
python production_bot.py --timeframe 15 --interval 60 --auto
```
⚠️ **WARNING**: Auto-trading should only be used with demo accounts

### Command Line Options
- `--timeframe`: Chart timeframe in minutes (default: 15)
- `--interval`: Scan interval in seconds (default: 60)
- `--auto`: Enable automatic trade execution (demo only)

### Telegram Integration
The bot sends Telegram alerts when patterns are detected:
- Pattern type and direction (bullish/bearish)
- Entry price, stop loss, and take profit levels
- Risk/reward ratio
- Current market conditions
- Real-time notifications when patterns match

## Supported Patterns (11 Total)
1. **Bullish Engulfing** - Reversal pattern at support
2. **Bearish Engulfing** - Reversal pattern at resistance
3. **Hammer** - Bullish reversal with long lower wick
4. **Shooting Star** - Bearish reversal with long upper wick
5. **Morning Star** - Three-candle bullish reversal
6. **Evening Star** - Three-candle bearish reversal
7. **Falling Wedge** - Bullish continuation pattern
8. **Rising Wedge** - Bearish reversal pattern
9. **Ascending Triangle** - Bullish continuation pattern
10. **Descending Triangle** - Bearish continuation pattern
11. **Double Bottom** - Bullish reversal pattern

## Key Features

### MarketDataFetcher
- Connects to MT5
- Fetches multiple timeframes (1m, 5m, 15m, 30m, 1h, 4h, D1)
- Returns clean pandas DataFrames
- Gets current bid/ask prices

### PatternDetector
- Detects 11 different candlestick and chart patterns
- Calculates technical indicators (RSI, EMA, ATR, Volume MA)
- Applies quality filters (RSI, trend, volume, ATR)
- Integrates support/resistance confirmation
- Returns high-probability setups only
- High-precision mode with pattern allowlist for >=60% win-rate

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
- Configurable timeframes and scan intervals
- Real-time Telegram notifications for pattern matches
- Applies all filters in real-time
- Alert-only mode for manual trading
- Optional auto-execution (demo only)
- Supports 11 different pattern types

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

## Quick Start Guide

### 1. Setup Environment
```powershell
# Create and activate virtual environment
py -3.10 -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Telegram (Optional)
Set up your `.env` file with Telegram credentials for real-time alerts.

### 3. Run Comprehensive Backtest
```powershell
python comprehensive_backtest.py
```
This validates all 11 patterns and shows which ones perform best.

### 4. Start Production Bot
```powershell
# Alert-only mode (recommended)
python production_bot.py --timeframe 15 --interval 60

# Auto-trading mode (demo only)
python production_bot.py --timeframe 15 --interval 60 --auto
```

## Important Notes
- **Python Version**: Requires Python 3.10
- **MT5 Requirement**: MetaTrader 5 must be running for data fetching
- **Demo Account**: Free and unlimited, recommended for testing
- **Time Zones**: All times are in MT5 server time
- **Market Conditions**: Spread varies with market conditions
- **Risk Management**: Always use stop losses and proper position sizing
- **Telegram Alerts**: Real-time notifications when patterns match your criteria
