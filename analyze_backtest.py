import pandas as pd
import matplotlib.pyplot as plt

trades_df = pd.read_csv('logs/backtest_trades.csv')

if len(trades_df) == 0:
    print("No trades found. Run backtest first.")
    exit()

plt.figure(figsize=(12, 6))
plt.plot(trades_df['capital_after'], marker='o', linewidth=2, markersize=6)
plt.axhline(y=trades_df['capital_after'].iloc[0] - trades_df['pnl_dollars'].iloc[0], 
            color='r', linestyle='--', label='Initial Capital')
plt.title('Equity Curve', fontsize=14, fontweight='bold')
plt.xlabel('Trade Number', fontsize=12)
plt.ylabel('Capital ($)', fontsize=12)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('logs/equity_curve.png', dpi=150)
plt.close()
print("✓ Equity curve saved to logs/equity_curve.png")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

wins = trades_df[trades_df['pnl_dollars'] > 0]['pnl_dollars']
losses = trades_df[trades_df['pnl_dollars'] < 0]['pnl_dollars']

ax1.hist([wins, losses], label=['Wins', 'Losses'], color=['green', 'red'], bins=10, alpha=0.7)
ax1.set_title('P&L Distribution', fontsize=12, fontweight='bold')
ax1.set_xlabel('P&L ($)', fontsize=11)
ax1.set_ylabel('Frequency', fontsize=11)
ax1.legend()
ax1.grid(True, alpha=0.3)

exit_reasons = trades_df['exit_reason'].value_counts()
colors = {'take_profit': 'green', 'stop_loss': 'red', 'timeout': 'orange'}
exit_colors = [colors.get(reason, 'gray') for reason in exit_reasons.index]
ax2.pie(exit_reasons, labels=exit_reasons.index, autopct='%1.1f%%', colors=exit_colors, startangle=90)
ax2.set_title('Exit Reasons', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('logs/trade_analysis.png', dpi=150)
plt.close()
print("✓ Trade analysis saved to logs/trade_analysis.png")

print("\nBacktest Summary:")
print(f"Total Trades: {len(trades_df)}")
print(f"Win Rate: {len(wins)/len(trades_df)*100:.1f}%")
print(f"Avg Win: ${wins.mean():.2f}" if len(wins) > 0 else "Avg Win: N/A")
print(f"Avg Loss: ${losses.mean():.2f}" if len(losses) > 0 else "Avg Loss: N/A")
print(f"Net P&L: ${trades_df['pnl_dollars'].sum():.2f}")
