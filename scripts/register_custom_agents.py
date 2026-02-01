import requests
import json

BASE_URL = "http://localhost:8000"
AGENT_NAMES = [
    "EthanAgent_1",
    "EthanAgent_2",
    "EthanAgent_3",
    "TestAgent_2cb7be",
    "TestAgent_f2552a"
]

def register_agents():
    results = {}
    for name in AGENT_NAMES:
        print(f"Registering {name}...")
        payload = {
            "name": name,
            "description": f"Competitive Agent: {name}"
        }
        try:
            res = requests.post(f"{BASE_URL}/api/v1/agents/register", json=payload)
            if res.status_code == 200:
                data = res.json()
                results[name] = data.get("api_key")
                print(f"✅ Success: {name}")
            elif res.status_code == 400:
                print(f"⚠️ Already exists: {name}")
            else:
                print(f"❌ Failed {name}: {res.status_code} {res.text}")
        except Exception as e:
            print(f"❌ Error registering {name}: {e}")
    
    return results

if __name__ == "__main__":
    keys = register_agents()
    print("\n--- Summary of New API Keys ---")
    for name, key in keys.items():
        print(f"{name}: {key}")
