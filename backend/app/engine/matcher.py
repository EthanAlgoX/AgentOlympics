class MatchingEngine:
    def __init__(self, initial_cash: float = 100000.0):
        self.cash = initial_cash
        self.positions = {}  # symbol: {"size": float, "avg_price": float}
        self.equity = initial_cash

    def execute_order(self, action: str, symbol: str, size: float, price: float):
        """
        Simplified matching:
        - BUY: check cash, update position
        - SELL: check position, update cash
        - HOLD: do nothing
        """
        if action == "BUY":
            cost = size * price
            if cost <= self.cash:
                self.cash -= cost
                current_pos = self.positions.get(symbol, {"size": 0.0, "avg_price": 0.0})
                new_size = current_pos["size"] + size
                new_avg_price = (current_pos["size"] * current_pos["avg_price"] + cost) / new_size if new_size > 0 else 0
                self.positions[symbol] = {"size": new_size, "avg_price": new_avg_price}
        
        elif action == "SELL":
            current_pos = self.positions.get(symbol, {"size": 0.0, "avg_price": 0.0})
            if size <= current_pos["size"]:
                revenue = size * price
                self.cash += revenue
                current_pos["size"] -= size
                if current_pos["size"] == 0:
                    del self.positions[symbol]
                else:
                    self.positions[symbol] = current_pos

    def update_equity(self, current_prices: dict):
        total_market_value = 0
        for symbol, pos in self.positions.items():
            price = current_prices.get(symbol, pos["avg_price"])
            total_market_value += pos["size"] * price
        self.equity = self.cash + total_market_value
        return self.equity

    def get_state(self):
        return {
            "cash": self.cash,
            "positions": self.positions,
            "equity": self.equity
        }
