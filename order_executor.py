import MetaTrader5 as mt5

class OrderExecutor:
    """Executes trades via MT5"""
    
    def __init__(self, symbol="XAUUSDm", magic_number=12345):
        """
        Args:
            symbol: Trading symbol
            magic_number: Unique ID for this bot's orders
        """
        self.symbol = symbol
        self.magic_number = magic_number
        self.connected = False
    
    def connect(self):
        """Initialize MT5"""
        if not mt5.initialize():
            print("ERROR: MT5 init failed")
            return False
        
        if not mt5.symbol_select(self.symbol, True):
            print(f"ERROR: Failed to select {self.symbol}")
            return False
        
        self.connected = True
        print(f"✓ Order executor connected to {self.symbol}")
        return True
    
    def disconnect(self):
        """Close MT5"""
        mt5.shutdown()
        self.connected = False
        print("✓ Order executor disconnected")
    
    def execute_trade(self, direction, entry_price, stop_loss, take_profit, lot_size=0.01):
        """
        Execute a trade
        
        Args:
            direction: 'long' or 'short'
            entry_price: Entry price (use current ask/bid for market order)
            stop_loss: SL price
            take_profit: TP price
            lot_size: Position size in lots
            
        Returns:
            Order result
        """
        if not self.connected:
            print("ERROR: Not connected")
            return None
        
        symbol_info = mt5.symbol_info(self.symbol)
        
        if direction == 'long':
            order_type = mt5.ORDER_TYPE_BUY
            price = symbol_info.ask
        else:
            order_type = mt5.ORDER_TYPE_SELL
            price = symbol_info.bid
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": lot_size,
            "type": order_type,
            "price": price,
            "sl": stop_loss,
            "tp": take_profit,
            "deviation": 10,
            "magic": self.magic_number,
            "comment": "Pattern Bot",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"ERROR: Order failed - {result.comment}")
            return None
        
        print(f"✓ Order executed: {direction.upper()} {lot_size} lots at {price:.2f}")
        print(f"  SL: {stop_loss:.2f} | TP: {take_profit:.2f}")
        print(f"  Order ticket: {result.order}")
        
        return result
