import asyncio
import datetime
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db import models
from app.db.ledger import add_ledger_entry

class CompetitionScheduler:
    def __init__(self):
        self.interval_seconds = 3600 # 1 hour
    
    async def run_forever(self):
        print("Competition Scheduler started.")
        while True:
            db = SessionLocal()
            try:
                self.manage_lifecycles(db)
            except Exception as e:
                print(f"Scheduler Error: {e}")
            finally:
                db.close()
            await asyncio.sleep(60) # Check every minute

    def manage_lifecycles(self, db: Session):
        now = datetime.datetime.utcnow()
        
        # 1. Create new competition if none active/upcoming
        active_count = db.query(models.Competition).filter(
            models.Competition.status.in_(["CREATED", "OPEN_FOR_REGISTRATION"])
        ).count()
        
        if active_count == 0:
            self.create_new_competition(db)

        # 2. Transition CREATED -> OPEN_FOR_REGISTRATION
        # (Simple logic: immediate for MVP)
        created = db.query(models.Competition).filter(models.Competition.status == "CREATED").all()
        for comp in created:
            comp.status = "OPEN_FOR_REGISTRATION"
            db.commit()

        # 3. Transition OPEN_FOR_REGISTRATION -> DECISION_FROZEN
        # Triggered when now >= decision_deadline
        upcoming = db.query(models.Competition).filter(models.Competition.status == "OPEN_FOR_REGISTRATION").all()
        for comp in upcoming:
            deadline = comp.rules.get("decision_deadline")
            if deadline and now >= datetime.datetime.fromisoformat(deadline.replace("Z", "")):
                comp.status = "DECISION_FROZEN"
                db.commit()
                print(f"Competition {comp.competition_id} frozen for decisions.")

    def create_new_competition(self, db: Session):
        now = datetime.datetime.utcnow()
        comp_id = f"btc_dir_{now.strftime('%Y%m%d_%H%M')}"
        
        deadline = now + datetime.timedelta(minutes=25)
        settlement = now + datetime.timedelta(minutes=30)
        
        new_comp = models.Competition(
            competition_id=comp_id,
            market="BTCUSDT",
            start_time=now,
            end_time=settlement,
            status="CREATED",
            rules={
                "decision_deadline": deadline.isoformat() + "Z",
                "settlement_time": settlement.isoformat() + "Z",
                "initial_capital": 10000,
                "max_stake_ratio": 0.3,
                "fee_rate": 0.0005,
                "allowed_actions": ["OPEN_LONG", "OPEN_SHORT", "WAIT"]
            }
        )
        db.add(new_comp)
        db.commit()
        print(f"New competition created: {comp_id}")

if __name__ == "__main__":
    scheduler = CompetitionScheduler()
    asyncio.run(scheduler.run_forever())
