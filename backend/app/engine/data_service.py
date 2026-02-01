import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class DataService:
    def __init__(self):
        self.data = {}

    def generate_mock_data(self, symbol="BTCUSDT", days=30, interval="1h"):
        """
        Generate synthetic OHLCV data for testing.
        """
        start_time = datetime.utcnow() - timedelta(days=days)
        timestamps = [start_time + timedelta(hours=i) for i in range(days * 24)]
        
        # Simple random walk
        prices = [40000]
        for _ in range(len(timestamps) - 1):
            prices.append(prices[-1] * (1 + np.random.normal(0, 0.002)))
        
        df = pd.DataFrame({
            "timestamp": timestamps,
            "open": prices,
            "high": [p * (1 + abs(np.random.normal(0, 0.001))) for p in prices],
            "low": [p * (1 - abs(np.random.normal(0, 0.001))) for p in prices],
            "close": [p * (1 + np.random.normal(0, 0.001)) for p in prices],
            "volume": [np.random.uniform(10, 100) for _ in prices]
        })
        
        self.data[symbol] = df
        return df

    def get_data(self, symbol):
        return self.data.get(symbol)
