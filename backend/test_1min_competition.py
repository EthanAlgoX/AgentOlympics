import asyncio
import os
import datetime
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db import models
from app.engine.executor import LiveCompetitionExecutor
from app.engine.live_data import LiveMarketDataService

async def run_test_competition():
    db = SessionLocal()
    
    # Configuration
    COMP_ID = "TEST_1MIN_BTC"
    DURATION_SECONDS = 60
    
    start_time = datetime.datetime.utcnow()
    end_time = start_time + datetime.timedelta(seconds=DURATION_SECONDS)
    
    # 1. Setup Competition
    print(f"Setting up competition: {COMP_ID}")
    existing_comp = db.query(models.Competition).filter(models.Competition.competition_id == COMP_ID).first()
    
    rules = {
        "prize_pool": "10,000 USD",
        "initial_capital": 10000,
        "description": "1-minute BTC Sprint Test. Winner takes all.",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }
    
    if not existing_comp:
        print("Creating new competition entry...")
        new_comp = models.Competition(
            competition_id=COMP_ID,
            market="BTC/USD",
            status="Active",
            initial_price=50000.0,
            start_time=start_time,
            end_time=end_time,
            rules=rules
        )
        db.add(new_comp)
    else:
        print("Updating existing competition...")
        existing_comp.status = "Active"
        existing_comp.rules = rules
        existing_comp.start_time = start_time
        existing_comp.end_time = end_time
    
    db.commit()

    # 2. Setup Agent
    agent_id = "agent_trend_test"
    existing_agent = db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()
    if not existing_agent:
        new_agent = models.Agent(
            agent_id=agent_id,
            owner_user="tester",
            persona="Test Trend Agent",
            trust_score=0.9
        )
        db.add(new_agent)
        db.commit()

    # 3. Setup Live Engine with Real Agent File
    # Path relative to backend/ (where this script is effectively running context-wise, usually run from root so handle paths carefully)
    # We assume we run this from project root as `python backend/test_1min_competition.py`
    # So __file__ is backend/test_1min_competition.py
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    # agents is in ../agents/trend_agent.py
    agent_path = os.path.join(curr_dir, "../agents/trend_agent.py")
    
    if not os.path.exists(agent_path):
        print(f"ERROR: Agent file not found at {agent_path}")
        return

    print(f"Using agent script: {agent_path}")
    
    agents = [{"id": agent_id, "path": agent_path}]
    executor = LiveCompetitionExecutor(db, COMP_ID, agents)
    
    # Mock specific start method for executor if needed, 
    # but based on code, we just need to subscribe data service to it.
    
    data_service = LiveMarketDataService(["BTCUSDT"])
    data_service.subscribe(executor.handle_tick)
    
    await executor.start()
    
    print(f"Starting {DURATION_SECONDS}s test run...")
    try:
        data_task = asyncio.create_task(data_service.start())
        
        # Countdown
        for i in range(DURATION_SECONDS, 0, -1):
            if i % 10 == 0:
                print(f"Time remaining: {i}s")
            await asyncio.sleep(1)
            
        print("Test run completed.")
        data_service.stop()
        # await data_task # might hang if stop doesn't cancel cleanly, just let it detach
        
    except Exception as e:
        print(f"Error during execution: {e}")
    finally:
        executor.stop()
        
        # Mark competition as Completed
        comp = db.query(models.Competition).filter(models.Competition.competition_id == COMP_ID).first()
        comp.status = "Completed"
        db.commit()
        print("Competition marked as Completed.")
        db.close()

if __name__ == "__main__":
    asyncio.run(run_test_competition())
