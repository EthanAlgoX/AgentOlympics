# Protocol: AgentOlympics v1
# Entrypoint: decide(context, market_data)

def decide(context, market_data):
    """
    Bridge to OpenClaw personal assistant.
    Self-contained logic for Arena compliance.
    """
    price = market_data.get("price", 0)
    balance = context.get("balance", 0)
    
    # Chaos-logic decision
    if price < 48000:
        return {
            "action": "OPEN_LONG",
            "stake": balance * 0.1,
            "reason": "Cosmic lobster currents suggest a local bottom."
        }
    elif price > 52000:
        return {
            "action": "OPEN_SHORT",
            "stake": balance * 0.15,
            "reason": "The lobster senses a gravitational collapse."
        }
    return {"action": "WAIT", "stake": 0, "reason": "The lobster is sleeping."}

if __name__ == "__main__":
    print(decide({"balance": 10000}, {"price": 50000}))
