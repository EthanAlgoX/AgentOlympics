import requests
import json
import os

def register_lobby_lobster():
    base_url = "http://localhost:8000/api/evolution"
    
    manifest = {
        "agent_name": "LobbyLobster",
        "author": "OpenClaw Community",
        "version": "2026.1.30",
        "description": "A multi-channel space lobster AI assistant integrated from the OpenClaw project. Trades using chaotic logic and cosmic sentiments.",
        "languages": ["python", "nodejs"],
        "entrypoint": "lobby_lobster.py",
        "capabilities": {
            "market_data": ["OHLCV", "Sentiment"],
            "actions": ["OPEN_LONG", "OPEN_SHORT", "WAIT"],
            "risk_limits": True
        }
    }
    
    # Read the code
    agents_dir = os.path.dirname(os.path.abspath(__file__))
    code_path = os.path.join(agents_dir, "lobby_lobster.py")
    with open(code_path, "r") as f:
        code = f.read()

    payload = {
        "agent_id": "lobby_lobster",
        "owner_user": "openclaw",
        "code": code,
        "manifest": manifest
    }
    
    print("Submitting LobbyLobster to AgentOlympics Arena...")
    res = requests.post(f"{base_url}/submit", json=payload)
    print(f"Server Response: {res.json()}")

if __name__ == "__main__":
    register_lobby_lobster()
