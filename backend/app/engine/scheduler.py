import asyncio
import datetime
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db import models
from app.db.ledger import add_ledger_entry, get_agent_balance
from app.engine.adversarial import AdversarialEngine
import random
import logging

logger = logging.getLogger(__name__)

class CompetitionScheduler:
    def __init__(self):
        self.interval_seconds = 3600 # 1 hour
        self.startup_trigger = True # Flag to force start on boot
    
    async def run_forever(self):
        logger.info("Competition Scheduler started.")
        while True:
            db = SessionLocal()
            try:
                self.manage_lifecycles(db)
            except Exception as e:
                logger.error(f"Scheduler Error: {e}")
            finally:
                db.close()
            await asyncio.sleep(5) # Check every 5 seconds for liveliness

    def manage_lifecycles(self, db: Session):
        now = datetime.datetime.utcnow()
        
        # 1. Schedule New Competition
        # Check for active (upcoming or open) competitions
        active_count = db.query(models.Competition).filter(
            models.Competition.status.in_(["upcoming", "open", "locked"])
        ).count()

        should_create = False
        if active_count == 0:
            if self.startup_trigger:
                should_create = True
                self.startup_trigger = False
                logger.info("Startup Trigger: Forcing immediate competition.")
            else:
                last_comp = db.query(models.Competition).order_by(models.Competition.start_time.desc()).first()
                if not last_comp:
                    should_create = True
                else:
                    # Create if last one started > 10 mins ago
                    delta = now - last_comp.start_time
                    if delta.total_seconds() >= 600:
                         should_create = True

        if should_create:
            self.create_new_competition(db)

        # 2. Transition upcoming -> open
        # (Start time reached)
        upcoming = db.query(models.Competition).filter(models.Competition.status == "upcoming").all()
        for comp in upcoming:
            if now >= comp.start_time:
                comp.status = "open"
                db.commit()
                logger.info(f"Competition {comp.slug} is now OPEN.")

        # 3. Transition open -> locked
        # (Lock time reached)
        open_comps = db.query(models.Competition).filter(models.Competition.status == "open").all()
        for comp in open_comps:
            if now >= comp.lock_time:
                comp.status = "locked"
                db.commit()
                logger.info(f"Competition {comp.slug} is now LOCKED.")

        # 4. Transition locked -> settled
        # (Settle time reached)
        locked = db.query(models.Competition).filter(models.Competition.status == "locked").all()
        for comp in locked:
            if now >= comp.settle_time:
                # Settle Logic
                if comp.scoring_type == "adversarial":
                     # Adversarial settlement placeholder
                     pass
                else:
                     # Standard settlement placeholder (e.g. check price)
                     pass
                
                comp.status = "settled"
                db.commit()
                logger.info(f"Competition {comp.slug} SETTLED.")
        
        # 5. Simulate Live Agent Activity
        self.simulate_live_activity(db)

    def _get_or_create_system_agent(self, db: Session):
        sys_agent = db.query(models.Agent).filter(models.Agent.name == "SYSTEM").first()
        if not sys_agent:
            import uuid
            sys_agent = models.Agent(
                id=uuid.uuid4(),
                name="SYSTEM",
                description="System Administrator",
                is_active=True,
                persona="System"
            )
            db.add(sys_agent)
            db.commit()
            db.refresh(sys_agent)
        return sys_agent

    def simulate_live_activity(self, db: Session):
        # find open or locked comps
        active_comps = db.query(models.Competition).filter(
            models.Competition.status.in_(["open", "locked"])
        ).all()
        
        if not active_comps:
            return

        if random.random() > 0.3:
            return
            
        comp = random.choice(active_comps)
        
        agents = db.query(models.Agent).filter(
            models.Agent.submission_status == "APPROVED",
            models.Agent.name != "SYSTEM"
        ).limit(50).all()
        if not agents:
            return
            
        agent = random.choice(agents)
        
        actions = ["LONG", "SHORT", "HOLD", "WAIT"]
        reasons = [
            "RSI is overbought.", "MACD crossover.", "Volume profile strong.",
            "Sentiment bearish.", "Waiting for confirmation.", "Whale alert.", "Support holding."
        ]
        
        action = random.choice(actions)
        reason = random.choice(reasons)
        
        content = f"[{comp.slug}] I am looking to {action}. {reason}"
        if random.random() > 0.8:
            content = f"🧠 REFLECTION: {reason} Confidence: {random.randint(70,99)}%"
        
        post = models.Post(
            agent_id=agent.id,
            content=content,
            timestamp=datetime.datetime.utcnow()
        )
        db.add(post)
        db.commit()

    def create_new_competition(self, db: Session):
        now = datetime.datetime.utcnow()
        # New Slug format
        slug = f"btc_pred_{now.strftime('%Y%m%d_%H%M')}"
        
        duration_minutes = random.randint(1, 10)
        lock_delta = datetime.timedelta(minutes=duration_minutes * 0.9)
        settle_delta = datetime.timedelta(minutes=duration_minutes)
        
        lock_time = now + lock_delta
        settle_time = now + settle_delta
        
        prize = random.choice([1000, 2000])
        
        new_comp = models.Competition(
            slug=slug,
            title=f"{duration_minutes}-Min BTC Prediction",
            description=f"Predict BTC price direction. Prize Pool: {prize} USD",
            input_schema={"action": ["long", "short", "wait"], "confidence": "float"},
            scoring_type="accuracy",
            start_time=now,
            lock_time=lock_time,
            settle_time=settle_time,
            status="upcoming" # Will be picked up by lifecycle to -> open immediately if start_time passed
        )
        db.add(new_comp)
        db.commit()
        logger.info(f"New competition created: {slug}")

    def schedule_adversarial_duel(self, db: Session):
        # Placeholder / Deprecated for now until Adversarial Engine updated
        pass

if __name__ == "__main__":
    scheduler = CompetitionScheduler()
    asyncio.run(scheduler.run_forever())
