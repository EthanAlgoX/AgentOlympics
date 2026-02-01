import requests

class PriceService:
    @staticmethod
    def get_current_price(symbol="BTCUSDT"):
        try:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            res = requests.get(url, timeout=5)
            data = res.json()
            return float(data["price"])
        except Exception as e:
            print(f"Error fetching price: {e}")
            return 50000.0 # Fallback

if __name__ == "__main__":
    print(PriceService.get_current_price())
