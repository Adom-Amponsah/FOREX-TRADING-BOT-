import mplfinance as mpf
import pandas as pd
import numpy as np

class ChartVisualizer:
    """Create candlestick charts"""
    
    @staticmethod
    def plot_candles(df, title="Gold Chart", save_path=None):
        """
        Plot candlestick chart
        
        Args:
            df: DataFrame with columns: time, open, high, low, close
            title: Chart title
            save_path: If provided, saves chart to this path
        """
        df_plot = df.copy()
        df_plot.set_index('time', inplace=True)
        
        mc = mpf.make_marketcolors(
            up='green', down='red',
            edge='inherit',
            wick='inherit',
            volume='in'
        )
        
        s = mpf.make_mpf_style(
            marketcolors=mc,
            gridstyle='-',
            y_on_right=False
        )
        
        mpf.plot(
            df_plot,
            type='candle',
            style=s,
            title=title,
            ylabel='Price (USD)',
            volume=False,
            savefig=save_path if save_path else None
        )
        
        if save_path:
            print(f"✓ Chart saved to {save_path}")
        else:
            print("✓ Chart displayed")
    
    @staticmethod
    def plot_with_signals(df, bullish_signals=[], bearish_signals=[], title="Gold Chart with Patterns"):
        """Plot chart with pattern markers"""
        df_plot = df.copy()
        df_plot.set_index('time', inplace=True)
        
        if bullish_signals:
            df_plot.loc[df.iloc[bullish_signals]['time'].values, 'Buy'] = [df.iloc[idx]['low'] * 0.999 for idx in bullish_signals]
        if bearish_signals:
            df_plot.loc[df.iloc[bearish_signals]['time'].values, 'Sell'] = [df.iloc[idx]['high'] * 1.001 for idx in bearish_signals]
        
        apds = []
        if 'Buy' in df_plot.columns:
            apds.append(mpf.make_addplot(df_plot['Buy'], type='scatter', markersize=100, marker='^', color='green'))
        if 'Sell' in df_plot.columns:
            apds.append(mpf.make_addplot(df_plot['Sell'], type='scatter', markersize=100, marker='v', color='red'))
        
        mc = mpf.make_marketcolors(
            up='green', down='red',
            edge='inherit',
            wick='inherit',
            volume='in'
        )
        
        s = mpf.make_mpf_style(
            marketcolors=mc,
            gridstyle='-',
            y_on_right=False
        )
        
        mpf.plot(
            df_plot[['open', 'high', 'low', 'close']], 
            type='candle',
            style=s,
            title=title,
            addplot=apds if apds else None,
            savefig='logs/patterns_marked.png'
        )
        
        print(f"✓ Chart with patterns saved to logs/patterns_marked.png")
