import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

if not mt5.initialize():
    print("MT5 initialization failed")
    quit()

print(f"MT5 version: {mt5.version()}")
print(f"MT5 terminal info: {mt5.terminal_info()}")

symbol = "XAUUSD"
if not mt5.symbol_select(symbol, True):
    print(f"Failed to select {symbol}")
    mt5.shutdown()
    quit()

symbol_info = mt5.symbol_info(symbol)
print(f"\n{symbol} Symbol Info:")
print(f"  Bid: {symbol_info.bid}")
print(f"  Ask: {symbol_info.ask}")
print(f"  Spread: {symbol_info.spread}")
print(f"  Digits: {symbol_info.digits}")

timeframe = mt5.TIMEFRAME_M15
num_candles = 200

rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_candles)

mt5.shutdown()

df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')

print(f"\nFetched {len(df)} candles:")
print(df.head(10))

print("\nMost recent candles:")
print(df.tail(5))

df.to_csv('logs/gold_data_test.csv', index=False)
print("\nData saved to logs/gold_data_test.csv")
