import asyncio
import time
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db import models
from app.engine.mutation import MutationEngine
import random

async def evolution_loop():
    """
    Automated worker that:
    1. Identifies top performing agents.
    2. Forks them to create new variants.
    3. Identifies struggling agents and 'mutates' them.
    """
    print("Evolution Worker started.")
    while True:
        db = SessionLocal()
        try:
            # 1. Identify top performing agents (by TrustScore)
            top_agents = db.query(models.Agent).order_by(models.Agent.trust_score.desc()).limit(2).all()
            for agent in top_agents:
                if random.random() < 0.2: # 20% chance to fork top performer
                    print(f"Auto-Evolution: Forking top performer {agent.agent_id}")
                    # Logic to trigger fork
                    pass

            # 2. Identify stagnant/struggling agents
            struggling = db.query(models.Agent).filter(models.Agent.trust_score < 0.4).limit(2).all()
            mutation_engine = MutationEngine(db)
            for agent in struggling:
                if random.random() < 0.5: # 50% chance to mutate
                    print(f"Auto-Evolution: Mutating struggling agent {agent.agent_id}")
                    # Mocking an LLM refinement
                    mutated_code = "# Auto-generated mutation\n# Goal: Stability improvement\n"
                    mutation_engine.apply_mutation(agent.agent_id, "system_evolution", mutated_code)

        except Exception as e:
            print(f"Evolution Worker Error: {e}")
        finally:
            db.close()
        
        await asyncio.sleep(60) # Run every minute

if __name__ == "__main__":
    asyncio.run(evolution_loop())
