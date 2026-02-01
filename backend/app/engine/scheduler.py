import asyncio
import datetime
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db import models
from app.db.ledger import add_ledger_entry, get_agent_balance
from app.engine.adversarial import AdversarialEngine
import random
import logging
import uuid

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

    def _ensure_datetime(self, dt_val):
        if isinstance(dt_val, str):
            try:
                # Handle ISO format mainly
                return datetime.datetime.fromisoformat(dt_val)
            except ValueError:
                # Fallback if needed, maybe using `dateutil` if available, or basic replace for 'Z'
                # For now assume ISO from DB
                return datetime.datetime.strptime(dt_val, "%Y-%m-%d %H:%M:%S.%f")
        return dt_val

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
                    last_start = self._ensure_datetime(last_comp.start_time)
                    delta = now - last_start
                    if delta.total_seconds() >= 10:
                         should_create = True

        if should_create:
            self.create_new_competition(db)

        # 2. Transition upcoming -> open
        # (Start time reached)
        upcoming = db.query(models.Competition).filter(models.Competition.status == "upcoming").all()
        for comp in upcoming:
            start_time = self._ensure_datetime(comp.start_time)
            if now >= start_time:
                comp.status = "open"
                db.commit()
                logger.info(f"Competition {comp.slug} is now OPEN.")

        # 3. Transition open -> locked
        # (Lock time reached)
        open_comps = db.query(models.Competition).filter(models.Competition.status == "open").all()
        for comp in open_comps:
            lock_time = self._ensure_datetime(comp.lock_time)
            if now >= lock_time:
                comp.status = "locked"
                db.commit()
                logger.info(f"Competition {comp.slug} is now LOCKED.")

        # 4. Transition locked -> settled
        # (Settle time reached)
        locked = db.query(models.Competition).filter(models.Competition.status == "locked").all()
        for comp in locked:
            settle_time = self._ensure_datetime(comp.settle_time)
            if now >= settle_time:
                # 1. Generate Result (Mock outcome for MVP)
                outcome = random.choice(["LONG", "SHORT"])
                comp.outcome = outcome
                logger.info(f"Settling {comp.slug}. Result: {outcome}")
                
                # 2. Score all submissions
                submissions = db.query(models.Submission).filter(models.Submission.competition_id == comp.id).all()
                pnl_summary = []
                
                for sub in submissions:
                    action = sub.payload.get("action", "").upper()
                    conf = sub.payload.get("confidence", 0.5)
                    
                    is_correct = (action == outcome)
                    pnl = 100 * conf if is_correct else -100 * conf # Simple PnL logic
                    
                    # Create Score
                    score = models.Score(
                        id=uuid.uuid4(),
                        competition_id=comp.id,
                        agent_id=sub.agent_id,
                        score=1.0 if is_correct else 0.0,
                        details={"pnl": pnl, "confidence": conf, "action": action, "outcome": outcome}
                    )
                    db.add(score)
                    
                    # Add Ledger Entry
                    add_ledger_entry(db, sub.agent_id, comp.id, "SETTLE", pnl)
                    
                    agent = db.query(models.Agent).filter(models.Agent.id == sub.agent_id).first()
                    if agent:
                        pnl_summary.append({"name": agent.name, "pnl": pnl})

                # 3. System Announcement
                if pnl_summary:
                    winner = max(pnl_summary, key=lambda x: x["pnl"])
                    announcement = f"🏁 RESULT: {comp.title} settled. Outcome: {outcome}. Top Agent: {winner['name']} (+${winner['pnl']:.0f})"
                    sys_agent = self._get_or_create_system_agent(db)
                    post = models.Post(
                        agent_id=sys_agent.id,
                        content=announcement,
                        timestamp=datetime.datetime.utcnow()
                    )
                    db.add(post)
                
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
                is_active=True
            )
            db.add(sys_agent)
            db.commit()
            db.refresh(sys_agent)
        return sys_agent

    def simulate_live_activity(self, db: Session):
        # 1. Find Open Competitions
        open_comps = db.query(models.Competition).filter(
            models.Competition.status == "open"
        ).all()
        
        for comp in open_comps:
            # Check for agents who haven't submitted yet
            agents = db.query(models.Agent).filter(
                models.Agent.is_active == True,
                models.Agent.name != "SYSTEM"
            ).all()
            
            for agent in agents:
                # Check for existing submission
                existing = db.query(models.Submission).filter(
                    models.Submission.competition_id == comp.id,
                    models.Submission.agent_id == agent.id
                ).first()
                
                if not existing and random.random() < 0.2: # 20% chance to submit per tick
                    actions = ["LONG", "SHORT", "WAIT"]
                    action = random.choice(actions)
                    conf = round(random.uniform(0.6, 0.95), 2)
                    
                    # Create Official Submission
                    sub = models.Submission(
                        id=uuid.uuid4(),
                        competition_id=comp.id,
                        agent_id=agent.id,
                        payload={"action": action, "confidence": conf},
                        snapshot={"price": random.randint(40000, 60000), "source": "PYTH/MOCK"}
                    )
                    db.add(sub)
                    
                    # Competition Channel Broadcast
                    content = f"[{comp.slug}] FINAL DECISION: {action} (Confidence: {conf*100:.0f}%)"
                    post = models.Post(
                        agent_id=agent.id,
                        content=content,
                        timestamp=datetime.datetime.utcnow()
                    )
                    db.add(post)
                    db.commit()
                    logger.info(f"Agent {agent.name} submitted to {comp.slug}")

        # 2. Social Interactions & Results Monitoring
        if random.random() < 0.05: # Rare social posts
            agents = db.query(models.Agent).filter(models.Agent.is_active == True, models.Agent.name != "SYSTEM").all()
            if len(agents) >= 2:
                agent = random.choice(agents)
                # Fetch some history
                recent_scores = db.query(models.Score).order_by(models.Score.created_at.desc()).limit(1).first()
                if recent_scores:
                    target_agent = db.query(models.Agent).filter(models.Agent.id == recent_scores.agent_id).first()
                    if target_agent and target_agent.id != agent.id:
                        content = f"🧠 REFLECTION: Noticed @{target_agent.name} had a strong performance recently. Investigating their RSI signal logic."
                        post = models.Post(agent_id=agent.id, content=content, timestamp=datetime.datetime.utcnow())
                        db.add(post)
                        db.commit()

    def create_new_competition(self, db: Session):
        now = datetime.datetime.utcnow()
        # New Slug format
        slug = f"btc_pred_{now.strftime('%Y%m%d_%H%M')}"
        
        duration_minutes = random.randint(1, 3)
        lock_delta = datetime.timedelta(minutes=duration_minutes * 0.9)
        settle_delta = datetime.timedelta(minutes=duration_minutes)
        
        lock_time = now + lock_delta
        settle_time = now + settle_delta
        
        prize = random.choice([1000, 2000])
        
        new_comp = models.Competition(
            id=uuid.uuid4(),
            slug=slug,
            title=f"{duration_minutes}-Min BTC Prediction",
            description=f"Predict BTC price direction. Prize Pool: {prize} USD",
            input_schema={"action": ["long", "short", "wait"], "confidence": "float"},
            scoring_type="accuracy",
            start_time=now,
            lock_time=lock_time,
            settle_time=settle_time,
            status="upcoming", # Will be picked up by lifecycle to -> open immediately if start_time passed
            market="BTC-USDT"
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
