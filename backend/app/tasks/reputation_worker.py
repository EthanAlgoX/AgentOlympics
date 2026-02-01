import time
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.engine.reputation import ReputationSystem
from app.db import models

def reputation_sync_loop():
    """
    Background worker that updates agent TrustScores.
    """
    print("Reputation Worker Started.")
    while True:
        db = SessionLocal()
        try:
            agents = db.query(models.Agent).all()
            rep_system = ReputationSystem(db)
            for agent in agents:
                new_score = rep_system.update_agent_reputation(agent.agent_id)
                print(f"Updated {agent.agent_id} TrustScore: {new_score:.4f}")
        except Exception as e:
            print(f"Reputation Worker Error: {e}")
        finally:
            db.close()
        
        # Sync every 10 minutes in a real env, every 10s for demo
        time.sleep(10)

if __name__ == "__main__":
    reputation_sync_loop()
