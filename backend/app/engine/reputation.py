import numpy as np
from sqlalchemy.orm import Session
from app.db import models
from datetime import datetime, timedelta

class ReputationSystem:
    def __init__(self, db: Session):
        self.db = db

    def calculate_trust_score(self, agent_id: str):
        """
        TrustScore = (Volatility_Adj_PnL * 0.4) + (Sharpe * 0.3) + (Stability * 0.2) + (Consistency * 0.1)
        """
        # Fetch snapshots for the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        snapshots = self.db.query(models.LeaderboardSnapshot)\
            .filter(models.LeaderboardSnapshot.agent_id == agent_id)\
            .filter(models.LeaderboardSnapshot.snapshot_at >= thirty_days_ago)\
            .order_by(models.LeaderboardSnapshot.snapshot_at.asc())\
            .all()

        if not snapshots:
            return 0.5 # Default middle score for new agents

        pnls = [s.pnl for s in snapshots]
        sharpes = [s.sharpe for s in snapshots]
        
        # 1. Volatility Adjusted PnL
        avg_pnl = np.mean(pnls)
        pnl_std = np.std(pnls) if len(pnls) > 1 else 0.01
        vol_adj_pnl = avg_pnl / (pnl_std + 0.0001)
        vol_adj_pnl_score = 1 / (1 + np.exp(-vol_adj_pnl)) # Sigmoid to [0, 1]

        # 2. Avg Sharpe
        avg_sharpe = np.mean(sharpes)
        sharpe_score = min(1.0, max(0, avg_sharpe / 4.0)) # Scaled assuming 4 as "excellent"

        # 3. Stability (Normalized variance of PnL)
        stability_score = 1.0 - min(1.0, pnl_std * 2)

        # 4. Consistency (Percentage of profitable snapshots)
        positive_pnls = [p for p in pnls if p > 0]
        consistency_score = len(positive_pnls) / len(pnls)

        trust_score = (vol_adj_pnl_score * 0.4) + \
                      (sharpe_score * 0.3) + \
                      (stability_score * 0.2) + \
                      (consistency_score * 0.1)

        return float(trust_score)

    def update_agent_reputation(self, agent_id: str):
        new_score = self.calculate_trust_score(agent_id)
        agent = self.db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()
        if agent:
            agent.trust_score = new_score
            self.db.commit()
        return new_score
