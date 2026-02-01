import requests
import json
import time

def run_alignment_test():
    base_url = "http://localhost:8000/api"
    
    # 1. Fetch active competition
    print("Fetching active competition...")
    res = requests.get(f"{base_url}/leaderboard/global") # Use a different way to get comp if needed
    # Let's just assume we know one or fetch from a dedicated endpoint if we added it
    # For now, let's just trigger a manual mock cycle
    
    # 2. Mock a decision for agent_trend_test
    print("Submitting formalized decision...")
    decision_data = {
        "action": "OPEN_LONG",
        "stake": 2000,
        "confidence": 0.95
    }
    # We need a real competition_id from the logs
    comp_id = "btc_dir_20260201_0721" # From previous step
    
    res = requests.post(f"{base_url}/agent/submit_decision/{comp_id}/agent_trend_test", json=decision_data)
    print(f"Decision Status: {res.status_code} - {res.text}")
    
    # 3. Verify Ledger (Self-Correction: Manual Check via SQL or API)
    # We'll check the leaderboard after we simulate settlement
    
if __name__ == "__main__":
    run_alignment_test()
