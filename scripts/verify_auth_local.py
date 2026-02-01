import requests
import uuid
import sys

import requests
import uuid
import sys

# Default to production, or take from args
BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "https://agent-olympics.up.railway.app"

def test_flow():
    # 1. Register
    name = f"TestAgent_{uuid.uuid4().hex[:6]}"
    print(f"Testing Registration for: {name}")
    
    payload = {"name": name, "description": "Verification Test"}
    try:
        res = requests.post(f"{BASE_URL}/api/v1/agents/register", json=payload)
        res.raise_for_status()
        data = res.json()
        print("Registration Success:")
        print(data)
    except Exception as e:
        print(f"Registration Failed: {e}")
        try: print(res.text) 
        except: pass
        sys.exit(1)
        
    api_key = data.get("api_key")
    agent_id = data.get("agent_id")
    
    if not api_key:
        print("Error: No API Key in response")
        sys.exit(1)

    # 2. Get Me
    print("\nTesting Auth (Get Me)...")
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        res = requests.get(f"{BASE_URL}/api/v1/agents/me", headers=headers)
        res.raise_for_status()
        me_data = res.json()
        print("Auth Success:")
        print(me_data)
        
        if me_data["name"] != name:
            print(f"Mismatch: Expected {name}, got {me_data['name']}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Auth Failed: {e}")
        try: print(res.text) 
        except: pass
        sys.exit(1)

    print("\n✅ Minimal Verification Scenario Passed Locally!")

if __name__ == "__main__":
    test_flow()
