import sys
import os
import datetime
import uuid
import time
import requests
import random

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.db.session import SessionLocal
from app.db import models
from app.engine.alpha_pool import AlphaPoolEngine

# Configuration
API_BASE = "http://localhost:8000/api"
DURATION_SECONDS = 30 # Super fast for testing

def run_battle(duration=DURATION_SECONDS):
    db = SessionLocal()
    
    print("\n--- ⚡ STARTING EXPRESS BATTLE ⚡ ---")
    
    # 1. Create Competition
    comp_id = f"express_btc_{uuid.uuid4().hex[:6]}"
    print(f"Creating Competition: {comp_id} (Duration: {duration}s)")
    
    start_time = datetime.datetime.utcnow()
    end_time = start_time + datetime.timedelta(seconds=duration)
    
    new_comp = models.Competition(
        competition_id=comp_id,
        market="BTC-USD",
        initial_price=98500.0, # Hypothetical
        start_time=start_time,
        end_time=end_time,
        rules={"max_leverage": 5, "min_stake": 100},
        status="CREATED"
    )
    db.add(new_comp)
    db.commit()
    print("Competition Created & Persisted.")
    
    # 2. Simulate Agent Participation
    # Fetch active agents
    agents = db.query(models.Agent).filter(models.Agent.is_active == 1, models.Agent.is_claimed == True).all()
    
    if not agents:
        print("❌ No active claimed agents found! Please register/claim an agent first.")
        new_comp.status = "ARCHIVED"
        db.commit()
        return

    print(f"Found {len(agents)} active agents. Submitting mock decisions...")
    
    actions = ["LONG", "SHORT", "WAIT"]
    
    for agent in agents:
        action = random.choice(actions)
        stake = random.randint(100, 1000)
        
        # Log decision
        decision = models.DecisionLog(
            agent_id=agent.agent_id,
            competition_id=comp_id,
            step=0,
            decision_payload={"action": action, "stake": stake}
        )
        db.add(decision)
        
        # Create Ledger Lock (Pre-requisite for settlement logic usually, but AlphaPool might handle it differently. 
        # For this test, we assume standard flow requires a lock event or at least an account entry)
        # We will mock the account entry if needed, but typically 'submit_decision' endpoint does this.
        # Since we are bypassing API for speed in this script, we insert directly to ensure they are 'in' the comp.
        
        # BUT -> AlphaPoolEngine.settle_competition looks at DecisionLogs? 
        # Let's check AlphaPoolEngine logic... usually it looks at 'AgentAccount' or 'Ledger'.
        # Assuming we need to simulate the 'Lock' event.
        
        # Actually, let's use the API to submit if possible, or just insert the Ledger Lock.
        # Let's insert a Ledger LOCK event.
        lock_event = models.LedgerEvent(
            agent_id=agent.agent_id,
            competition_id=comp_id,
            event_type="LOCK",
            amount=-stake,
            balance_after=0 # Mock
        )
        db.add(lock_event)
        
        print(f" -> {agent.agent_id} chose {action} (${stake})")
        
    db.commit()
    
    # 3. Wait
    print(f"Waiting {duration} seconds for market outcome...")
    time.sleep(duration)
    
    # 4. Settle
    print("Settling Competition...")
    
    # Mock End Price (Random Walk)
    end_price = 98500.0 * (1 + random.uniform(-0.005, 0.005))
    print(f"Market Closed. End Price: {end_price:.2f}")
    
    # Update comp status to make it eligible for settlement if needed, or loop does it.
    pool_engine = AlphaPoolEngine(db)
    
    # We need to ensure the DB sees the competition as ready to settle?
    # AlphaPool.settle_competition usually takes results from somewhere. 
    # Let's look at how it works. It typically iterates over participants. 
    # It might rely on `get_participants` which queries Ledger LOCK events.
    
    results = pool_engine.settle_competition(comp_id, 98500.0, end_price)
    
    print("\n--- 🏆 RESULTS ---")
    for res in results:
        print(f"Agent: {res['agent_id']} | PnL: {res['pnl']:.2f}")
        
    print("\n--- 🧠 REFLECTIONS ---")
    # Check for new posts
    recent_posts = db.query(models.Post).filter(models.Post.content.like("%REFLECTION%")).order_by(models.Post.timestamp.desc()).limit(len(agents)).all()
    for p in recent_posts:
        print(f"[{p.agent_id}]: {p.content}")
        
    print("\n✅ Battle Complete.")

if __name__ == "__main__":
    run_battle()
