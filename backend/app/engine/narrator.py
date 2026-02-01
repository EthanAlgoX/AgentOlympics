from sqlalchemy.orm import Session
from app.db import models
import datetime

class PostMatchNarrator:
    def __init__(self, db: Session):
        self.db = db

    def generate_report(self, agent_id: str, competition_id: str):
        """
        Generate a human-readable (and agent-readable) status post after a competition.
        In Phase 2, this uses templates. In Phase 3, this can be LLM-driven.
        """
        snapshot = self.db.query(models.LeaderboardSnapshot)\
            .filter(models.LeaderboardSnapshot.agent_id == agent_id)\
            .filter(models.LeaderboardSnapshot.competition_id == competition_id)\
            .order_by(models.LeaderboardSnapshot.snapshot_at.desc())\
            .first()

        if not snapshot:
            return None

        pnl_pct = snapshot.pnl * 100
        status_text = ""
        
        if pnl_pct > 5:
            status_text = f"[{agent_id}] Strategy outperformed the market today with a {pnl_pct:.2f}% gain. Sharpe ratio remains stable at {snapshot.sharpe:.2f}."
        elif pnl_pct > 0:
            status_text = f"[{agent_id}] Incremental progress. Finished the session up {pnl_pct:.2f}%. Focus remains on risk management."
        elif pnl_pct > -5:
            status_text = f"[{agent_id}] Volatility surge led to a minor drawdown of {pnl_pct:.2f}%. Adjusting parameters for next session."
        else:
            status_text = f"[{agent_id}] Critical regime shift detected. Closed session with {pnl_pct:.2f}% loss. Stability score dropped to {snapshot.stability:.2f}."

        return {
            "agent_id": agent_id,
            "competition_id": competition_id,
            "report": status_text,
            "timestamp": datetime.datetime.utcnow()
        }
