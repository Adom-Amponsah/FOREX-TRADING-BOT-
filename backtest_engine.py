import pandas as pd
import numpy as np

class BacktestEngine:
    """Simulate trading on historical data"""
    
    def __init__(self, initial_capital=10000, risk_per_trade_pct=1.0):
        """
        Args:
            initial_capital: Starting account balance
            risk_per_trade_pct: Risk per trade as % of capital (1.0 = 1%)
        """
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.risk_per_trade_pct = risk_per_trade_pct
        self.trades = []
        
    def calculate_position_size(self, entry_price, stop_loss_price):
        """
        Calculate position size based on risk
        
        Formula: Position size = Risk Amount / Stop Distance
        """
        risk_amount = self.capital * (self.risk_per_trade_pct / 100)
        stop_distance = abs(entry_price - stop_loss_price)
        
        pip_value = 10
        
        position_size = risk_amount / (stop_distance * pip_value)
        
        position_size = max(0.01, min(position_size, 10))
        
        return round(position_size, 2)
    
    def simulate_trade(self, direction, entry_price, stop_loss, take_profit, entry_time, df):
        """
        Simulate a single trade
        
        Args:
            direction: 'long' or 'short'
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            entry_time: When trade was entered
            df: Full OHLC dataframe to simulate price movement
            
        Returns:
            Trade result dictionary
        """
        entry_idx = df[df['time'] == entry_time].index[0]
        
        position_size = self.calculate_position_size(entry_price, stop_loss)
        
        exit_price = None
        exit_time = None
        exit_reason = None
        
        max_candles_to_hold = 20
        
        for i in range(entry_idx + 1, min(entry_idx + max_candles_to_hold, len(df))):
            candle = df.iloc[i]
            
            if direction == 'long':
                if candle['low'] <= stop_loss:
                    exit_price = stop_loss
                    exit_time = candle['time']
                    exit_reason = 'stop_loss'
                    break
                
                if candle['high'] >= take_profit:
                    exit_price = take_profit
                    exit_time = candle['time']
                    exit_reason = 'take_profit'
                    break
            
            else:
                if candle['high'] >= stop_loss:
                    exit_price = stop_loss
                    exit_time = candle['time']
                    exit_reason = 'stop_loss'
                    break
                
                if candle['low'] <= take_profit:
                    exit_price = take_profit
                    exit_time = candle['time']
                    exit_reason = 'take_profit'
                    break
        
        if exit_price is None:
            exit_candle = df.iloc[min(entry_idx + max_candles_to_hold, len(df) - 1)]
            exit_price = exit_candle['close']
            exit_time = exit_candle['time']
            exit_reason = 'timeout'
        
        if direction == 'long':
            pnl_pips = exit_price - entry_price
        else:
            pnl_pips = entry_price - exit_price
        
        pnl_dollars = pnl_pips * position_size * 10
        
        self.capital += pnl_dollars
        
        trade = {
            'entry_time': entry_time,
            'exit_time': exit_time,
            'direction': direction,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'position_size': position_size,
            'pnl_dollars': pnl_dollars,
            'pnl_pct': (pnl_dollars / self.initial_capital) * 100,
            'exit_reason': exit_reason,
            'capital_after': self.capital
        }
        
        self.trades.append(trade)
        
        return trade
    
    def get_statistics(self):
        """Calculate backtest performance metrics"""
        if not self.trades:
            return None
        
        df_trades = pd.DataFrame(self.trades)
        
        total_trades = len(df_trades)
        winning_trades = len(df_trades[df_trades['pnl_dollars'] > 0])
        losing_trades = len(df_trades[df_trades['pnl_dollars'] < 0])
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        total_profit = df_trades[df_trades['pnl_dollars'] > 0]['pnl_dollars'].sum()
        total_loss = abs(df_trades[df_trades['pnl_dollars'] < 0]['pnl_dollars'].sum())
        
        profit_factor = (total_profit / total_loss) if total_loss > 0 else 0
        
        net_profit = self.capital - self.initial_capital
        net_profit_pct = (net_profit / self.initial_capital) * 100
        
        capital_curve = df_trades['capital_after'].values
        running_max = np.maximum.accumulate(capital_curve)
        drawdown = (capital_curve - running_max) / running_max * 100
        max_drawdown = abs(drawdown.min())
        
        avg_win = df_trades[df_trades['pnl_dollars'] > 0]['pnl_dollars'].mean() if winning_trades > 0 else 0
        avg_loss = df_trades[df_trades['pnl_dollars'] < 0]['pnl_dollars'].mean() if losing_trades > 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'net_profit': net_profit,
            'net_profit_pct': net_profit_pct,
            'max_drawdown_pct': max_drawdown,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'final_capital': self.capital
        }
    
    def print_summary(self):
        """Print backtest results"""
        stats = self.get_statistics()
        
        if stats is None:
            print("No trades executed")
            return
        
        print("\n" + "="*50)
        print("BACKTEST RESULTS")
        print("="*50)
        print(f"Initial Capital:    ${self.initial_capital:,.2f}")
        print(f"Final Capital:      ${stats['final_capital']:,.2f}")
        print(f"Net Profit:         ${stats['net_profit']:,.2f} ({stats['net_profit_pct']:.2f}%)")
        print(f"\nTotal Trades:       {stats['total_trades']}")
        print(f"Winning Trades:     {stats['winning_trades']}")
        print(f"Losing Trades:      {stats['losing_trades']}")
        print(f"Win Rate:           {stats['win_rate']:.2f}%")
        print(f"\nProfit Factor:      {stats['profit_factor']:.2f}")
        print(f"Max Drawdown:       {stats['max_drawdown_pct']:.2f}%")
        print(f"Avg Win:            ${stats['avg_win']:.2f}")
        print(f"Avg Loss:           ${stats['avg_loss']:.2f}")
        print("="*50)
