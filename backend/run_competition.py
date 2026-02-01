import asyncio
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db import models
from app.engine.data_service import DataService
from app.engine.executor import CompetitionExecutor
import os

async def run_test_competition():
    db = SessionLocal()
    
    # 1. Setup Competition
    comp_id = "test_backtest_v1"
    existing_comp = db.query(models.Competition).filter(models.Competition.competition_id == comp_id).first()
    if not existing_comp:
        new_comp = models.Competition(
            competition_id=comp_id,
            market="crypto",
            start_time=None,
            end_time=None,
            rules={"initial_cash": 100000},
            status="Running"
        )
        db.add(new_comp)
        db.commit()

    # 2. Setup Agent
    agent_id = "agent_trend_test"
    existing_agent = db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()
    if not existing_agent:
        new_agent = models.Agent(
            agent_id=agent_id,
            owner_user="ethan",
            persona="Test Trend Agent",
            trust_score=0.8
        )
        db.add(new_agent)
        db.commit()

    # 3. Generate Data
    ds = DataService()
    market_data = ds.generate_mock_data(days=5) # 5 days for quick test
    
    # 4. Run Executor
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    agent_path = os.path.join(curr_dir, "../agents/trend_agent.py")
    agents = [{"id": agent_id, "path": agent_path}]
    # Adjust path if needed
    executor = CompetitionExecutor(db, comp_id, market_data, agents)
    print(f"Starting competition {comp_id}...")
    results = await executor.run()
    
    print("Competition Finished.")
    print(f"Results: {results}")
    
    db.close()

if __name__ == "__main__":
    asyncio.run(run_test_competition())
