import asyncio
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.engine.mutation import MutationEngine
import sys
import os

async def test_mutation_lifecycle():
    db = SessionLocal()
    engine = MutationEngine(db)
    
    agent_id = "agent_trend_test"
    print(f"Testing mutation for {agent_id}...")
    
    # Simulate a mutation call
    new_agent, status = await engine.apply_mutation(agent_id, "ethan_admin")
    
    if new_agent:
        print(f"Mutation SUCCESS! New Agent: {new_agent.agent_id}")
        # Verify the file was created
        file_path = f"agents/{new_agent.agent_id}.py"
        if os.path.exists(file_path):
            print(f"File verified at {file_path}")
        else:
            print(f"Error: File NOT found at {file_path}")
    else:
        print(f"Mutation FAILED: {status}")
    
    db.close()

if __name__ == "__main__":
    asyncio.run(test_mutation_lifecycle())
