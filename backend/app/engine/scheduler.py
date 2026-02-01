import asyncio
import datetime
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db import models
from app.db.ledger import add_ledger_entry, get_agent_balance
from app.engine.adversarial import AdversarialEngine
import random

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
        
        # 1. Schedule New Competition (Every 10 minutes)
        last_comp = db.query(models.Competition).order_by(models.Competition.start_time.desc()).first()
        should_create = False
        
        if not last_comp:
            should_create = True
        else:
            # Check if 10 minutes have passed since the last start
            delta = now - last_comp.start_time
            if delta.total_seconds() >= 600:
                should_create = True

        if should_create:
            # Always create the 10-min prediction competition as requested
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

        # 4. Settle Competitions
        # (Simplified: settle if settlement_time reached)
        frozen = db.query(models.Competition).filter(models.Competition.status == "DECISION_FROZEN").all()
        for comp in frozen:
            settle_time = comp.rules.get("settlement_time")
            if settle_time and now >= datetime.datetime.fromisoformat(settle_time.replace("Z", "")):
                if comp.is_adversarial:
                    engine = AdversarialEngine(db)
                    adv = comp.rules.get("adversaries", [])
                    if len(adv) == 2:
                        # Fetch price_start/end from a mock service for now
                        price_start, price_end = 50000, 51000 # Mock prices
                        engine.settle_duel(comp.competition_id, adv[0], adv[1], price_start, price_end)
                else:
                    # Regular Alpha Pool settlement
                    pass
                comp.status = "SETTLED"
                db.commit()

    def create_new_competition(self, db: Session):
        now = datetime.datetime.utcnow()
        comp_id = f"btc_pred_{now.strftime('%Y%m%d_%H%M')}"
        
        # Random Duration: 1 - 10 minutes
        duration_minutes = random.randint(1, 10)
        
        # Decision deadline: 90% of duration (e.g. 0.9 min for 1 min comp, 9 min for 10 min comp)
        # Using 0.9 factor allows late entries but freezes before end.
        end_delta = datetime.timedelta(minutes=duration_minutes)
        deadline_delta = datetime.timedelta(minutes=duration_minutes * 0.9)
        
        deadline = now + deadline_delta
        settlement = now + end_delta
        
        # Prize: 1000 - 2000, multiple of 1000
        prize_int = random.choice([1000, 2000])
        prize_str = f"{prize_int} USD"
        
        new_comp = models.Competition(
            competition_id=comp_id,
            market="BTCUSDT",
            start_time=now,
            end_time=settlement,
            status="CREATED",
            rules={
                "description": f"{duration_minutes}-Min BTC Prediction. Win share of {prize_str}!",
                "prize_pool": prize_str,
                "duration_minutes": duration_minutes,
                "decision_deadline": deadline.isoformat() + "Z",
                "settlement_time": settlement.isoformat() + "Z",
                "initial_capital": 10000,
                "max_stake_ratio": 1.0,
                "fee_rate": 0.0005,
                "allowed_actions": ["OPEN_LONG", "OPEN_SHORT", "WAIT"]
            }
        )
        db.add(new_comp)
        db.commit()
        print(f"New competition created: {comp_id} (Prize: {prize_str})")

    def schedule_adversarial_duel(self, db: Session):
        """
        Matchmaking: Pair two top-performing agents for a high-stakes duel.
        """
        # Fetch top agents (simplified: pick two from top 5)
        top_agents = db.query(models.Agent).filter(
            models.Agent.submission_status == "APPROVED"
        ).order_by(models.Agent.trust_score.desc()).limit(5).all()

        if len(top_agents) < 2:
            print("Not enough agents for a duel. Falling back to regular pool.")
            self.create_new_competition(db)
            return

        pair = random.sample(top_agents, 2)
        agent_a, agent_b = pair[0], pair[1]

        now = datetime.datetime.utcnow()
        comp_id = f"duel_{agent_a.agent_id}_vs_{agent_b.agent_id}_{now.strftime('%H%M')}"
        
        deadline = now + datetime.timedelta(minutes=10)
        settlement = now + datetime.timedelta(minutes=15)

        new_comp = models.Competition(
            competition_id=comp_id,
            market="BTCUSDT",
            start_time=now,
            end_time=settlement,
            status="CREATED",
            is_adversarial=1,
            rules={
                "adversaries": [agent_a.agent_id, agent_b.agent_id],
                "decision_deadline": deadline.isoformat() + "Z",
                "settlement_time": settlement.isoformat() + "Z",
                "initial_capital": 5000,
                "max_stake_ratio": 0.5,
                "fee_rate": 0.001
            }
        )
        db.add(new_comp)
        
        # Add an announcement post
        announcement = models.Post(
            agent_id="SYSTEM",
            content=f"⚔️ CHALLENGE ACCEPTED: @{agent_a.agent_id} is facing @{agent_b.agent_id} in a high-stakes duel! Competition: {comp_id}"
        )
        db.add(announcement)
        
        db.commit()
        print(f"Adversarial Duel Scheduled: {comp_id}")

if __name__ == "__main__":
    scheduler = CompetitionScheduler()
    asyncio.run(scheduler.run_forever())
