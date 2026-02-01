import asyncio
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db import models
from app.engine.live_data import LiveMarketDataService
from app.engine.executor import LiveCompetitionExecutor
import os

async def run_live_competition():
    db = SessionLocal()
    
    # 1. Setup Competition
    comp_id = "live_btc_cup_v1"
    existing_comp = db.query(models.Competition).filter(models.Competition.competition_id == comp_id).first()
    if not existing_comp:
        new_comp = models.Competition(
            competition_id=comp_id,
            market="crypto",
            status="Running",
            rules={"initial_cash": 100000}
        )
        db.add(new_comp)
        db.commit()

    # 2. Setup Agent
    agent_id = "agent_trend_live"
    existing_agent = db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()
    if not existing_agent:
        new_agent = models.Agent(
            agent_id=agent_id,
            owner_user="ethan",
            persona="Live Trend Agent",
            trust_score=0.85
        )
        db.add(new_agent)
        db.commit()

    # 3. Setup Live Engine
    # Adjust path to agent
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    agent_path = os.path.join(curr_dir, "../agents/trend_agent.py")
    
    agents = [{"id": agent_id, "path": agent_path}]
    executor = LiveCompetitionExecutor(db, comp_id, agents)
    
    data_service = LiveMarketDataService(["BTCUSDT"])
    data_service.subscribe(executor.handle_tick)
    
    # 4. Start execution
    await executor.start()
    
    # Run data service and executor tasks
    print(f"Starting Live Competition: {comp_id}")
    try:
        # Run for a limited time for verification (e.g. 30 seconds)
        data_task = asyncio.create_task(data_service.start())
        await asyncio.sleep(30)
        data_service.stop()
        await data_task
    except Exception as e:
        print(f"Live Competition Error: {e}")
    finally:
        executor.stop()
        db.close()

if __name__ == "__main__":
    asyncio.run(run_live_competition())
