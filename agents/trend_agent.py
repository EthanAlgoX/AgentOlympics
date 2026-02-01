import sys
import json

def on_tick(tick_data):
    """
    Very simple trend-following strategy:
    - If current price > previous open, BUY.
    - If current price < previous open, SELL.
    """
    market = tick_data["market"]
    ohlcv = market["ohlcv"][0]
    open_price = ohlcv[1]
    close_price = ohlcv[4]
    
    if close_price > open_price:
        return {"action": "BUY", "symbol": "BTCUSDT", "size": 0.1, "confidence": 0.8, "thought": "Price trending up (Close > Open). Bullish signal detected.", "reason": "Price trending up"}
    elif close_price < open_price:
        return {"action": "SELL", "symbol": "BTCUSDT", "size": 0.1, "confidence": 0.6, "thought": "Price trending down (Close < Open). Bearish divergence.", "reason": "Price trending down"}
    else:
        return {"action": "HOLD", "symbol": "BTCUSDT", "size": 0, "confidence": 0.5, "thought": "Market is flat. Waiting for volatility.", "reason": "No clear trend"}

def main():
    for line in sys.stdin:
        try:
            tick_data = json.loads(line)
            decision = on_tick(tick_data)
            print(json.dumps(decision))
            sys.stdout.flush()
        except Exception as e:
            # Errors shouldn't crash the agent in a loop
            print(json.dumps({"action": "HOLD", "error": str(e)}))
            sys.stdout.flush()

if __name__ == "__main__":
    main()
