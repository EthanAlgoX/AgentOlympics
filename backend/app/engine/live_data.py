import asyncio
import random
import datetime
from typing import Dict, List, Callable

class LiveMarketDataService:
    """
    Simulated live market data service that broadcasts price updates to subscribers.
    """
    def __init__(self, symbols: List[str]):
        self.symbols = symbols
        self.prices = {symbol: 40000.0 for symbol in symbols}
        self.subscribers: List[Callable] = []
        self._running = False

    async def start(self):
        self._running = True
        print(f"Live Market Data Service started for {self.symbols}")
        while self._running:
            for symbol in self.symbols:
                # Random walk simulation
                change = random.normalvariate(0, 0.0005)
                self.prices[symbol] *= (1 + change)
                
                tick = {
                    "symbol": symbol,
                    "price": self.prices[symbol],
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }
                
                # Broadcast to all subscribers
                for callback in self.subscribers:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(tick)
                    else:
                        callback(tick)
            
            await asyncio.sleep(1) # 1Hz updates

    def stop(self):
        self._running = False

    def subscribe(self, callback: Callable):
        self.subscribers.append(callback)

    def unsubscribe(self, callback: Callable):
        self.subscribers.remove(callback)
