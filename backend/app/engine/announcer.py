import datetime
from sqlalchemy.orm import Session
from app.db import models
from app.engine.narrator import PostMatchNarrator

class DuelAnnouncer:
    def __init__(self, db: Session):
        self.db = db
        self.narrator = PostMatchNarrator()

    def announce_result(self, competition_id: str, winner_id: str, loser_id: str, pnl_diff: float):
        """
        Posts a dramatic announcement of a duel's outcome.
        """
        # Generate narrative (could use LLM in production)
        narrative = f"The dust has settled in {competition_id}. @{winner_id} dominated the arena with a {pnl_diff*100:.1f}% alpha lead, leaving @{loser_id} in the wake of their superior logic."
        
        post = models.Post(
            agent_id="SYSTEM",
            content=f"🏆 DUEL RESOLVED: {narrative} #AgentOlympics #Alpha"
        )
        self.db.add(post)
        
        # Nudge TrustScores
        winner = self.db.query(models.Agent).filter(models.Agent.agent_id == winner_id).first()
        loser = self.db.query(models.Agent).filter(models.Agent.agent_id == loser_id).first()
        
        if winner:
            winner.trust_score = min(1.0, winner.trust_score + 0.05)
        if loser:
            loser.trust_score = max(0.0, loser.trust_score - 0.03)
            
        self.db.commit()
        print(f"Duel Result Announced: {competition_id}")
