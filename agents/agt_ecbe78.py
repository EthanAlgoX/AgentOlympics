
def decide(context, market_data):
    price = market_data.get("price", 0)
    if price < 50000:
        return {"action": "OPEN_LONG", "stake": 1000, "reason": "Bottom detected."}
    return {"action": "WAIT", "stake": 0}
    