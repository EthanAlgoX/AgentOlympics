import requests
import json

def test_full_submission_cycle():
    base_url = "http://localhost:8000/api/evolution"
    
    # 1. Test Valid Submission
    valid_payload = {
        "agent_id": "olympian_alpha",
        "owner_user": "ethan_dev",
        "code": "def on_data(context, market_data):\n    return {'action': 'OPEN_LONG', 'stake': 1000}",
        "manifest": {
            "agent_name": "Olympian Alpha",
            "author": "Ethan",
            "version": "1.0.0",
            "description": "A high-performance momentum agent."
        }
    }
    
    print("Testing Valid Submission...")
    res = requests.post(f"{base_url}/submit", json=valid_payload)
    print(f"Result: {res.json()}")

    # 2. Test Malicious Submission (Security Block)
    malicious_payload = valid_payload.copy()
    malicious_payload["agent_id"] = "hacker_agent"
    malicious_payload["code"] = "import os\nos.system('rm -rf /')"
    
    print("\nTesting Malicious Submission...")
    res = requests.post(f"{base_url}/submit", json=malicious_payload)
    print(f"Result (Should be Rejected): {res.json()}")

if __name__ == "__main__":
    test_full_submission_cycle()
