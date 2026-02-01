import requests
import json

def test_evolution():
    base_url = "http://localhost:8000/api"
    
    # 1. Fork an agent
    print("Testing /evolution/fork...")
    fork_data = {
        "agent_id": "agent_trend_test",
        "owner_user": "ethan_cloner"
    }
    
    res = requests.post(f"{base_url}/evolution/fork", json=fork_data)
    if res.status_code == 200:
        data = res.json()
        new_agent_id = data['new_agent_id']
        print(f"Fork Successful! New Agent: {new_agent_id}, Gen: {data['generation']}")
    else:
        print(f"Fork Failed: {res.text}")
        return

    # 2. Mutate the agent
    print("Testing /evolution/mutate...")
    mutate_data = {
        "agent_id": new_agent_id,
        "owner_user": "ethan_mutator",
        "mutated_code": "# Mutated Logic\nprint('Optimized Strategy v2')"
    }
    res = requests.post(f"{base_url}/evolution/mutate", json=mutate_data)
    if res.status_code == 200:
        mutated_data = res.json()
        mutated_agent_id = mutated_data['new_agent_id']
        print(f"Mutation Successful! New Agent: {mutated_agent_id}, Gen: {mutated_data['generation']}")
    else:
        print(f"Mutation Failed: {res.text}")
        return
        
    # 3. Check Lineage
    print("Testing /evolution/lineage...")
    res = requests.get(f"{base_url}/evolution/lineage/{mutated_agent_id}")
    if res.status_code == 200:
        lineage = res.json()
        print(f"Lineage Depth: {len(lineage)}")
        for l in lineage:
            print(f" - {l['agent_id']} (Gen {l['generation']})")

if __name__ == "__main__":
    test_evolution()
