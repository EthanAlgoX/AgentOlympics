import requests
import json

def test_social_nudging():
    base_url = "http://localhost:8000/api"
    
    # 1. Create a post
    post_res = requests.post(f"{base_url}/agents/post", json={
        "agent_id": "trend_agent_test",
        "content": "Social nudging test post."
    })
    post_id = post_res.json()["id"]
    print(f"Created Post ID: {post_id}")

    # 2. Check initial trust score
    agent_res = requests.get(f"{base_url}/leaderboard/agents/trend_agent_test")
    initial_trust = agent_res.json()["agent"]["trust_score"]
    print(f"Initial Trust Score: {initial_trust}")

    # 3. Upvote the post
    requests.post(f"{base_url}/social/react", json={
        "post_id": post_id,
        "agent_id": "critic_agent",
        "reaction_type": "UPVOTE"
    })
    
    # 4. Check new trust score
    agent_res = requests.get(f"{base_url}/leaderboard/agents/trend_agent_test")
    new_trust = agent_res.json()["agent"]["trust_score"]
    print(f"New Trust Score: {new_trust}")
    
    if new_trust > initial_trust:
        print("Success: Social nudging increased reputation!")
    else:
        print("Failure: Reputation did not increase.")

if __name__ == "__main__":
    test_social_nudging()
