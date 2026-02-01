from app.db import models
from app.db.ledger import add_ledger_entry
from sqlalchemy.orm import Session
import datetime

class AlphaPoolEngine:
    def __init__(self, db: Session):
        self.db = db

    def settle_competition(self, competition_id: str, price_start: float, price_end: float):
        """
        Settles a general Alpha Pool competition.
        Calculates PnL for every agent that submitted a decision.
        """
        comp = self.db.query(models.Competition).filter(models.Competition.competition_id == competition_id).first()
        if not comp:
            print(f"Competition {competition_id} not found.")
            return

        # Fetch all decisions
        decisions = self.db.query(models.DecisionLog).filter(models.DecisionLog.competition_id == competition_id).all()
        
        print(f"Settling Competition: {competition_id} | Start Price: {price_start} | End Price: {price_end}")
        
        results = []
        for dec in decisions:
            agent_id = dec.agent_id
            payload = dec.decision_payload
            action = payload.get("action", "WAIT")
            stake = payload.get("stake", 0)
            
            pnl = 0.0
            if action == "OPEN_LONG":
                pnl = stake * (price_end - price_start) / price_start
            elif action == "OPEN_SHORT":
                pnl = stake * (price_start - price_end) / price_start
            
            # Apply fees (mock 0.1% fee)
            fee = stake * comp.rules.get("fee_rate", 0.001)
            net_pnl = pnl - fee
            
            # Update Ledger
            add_ledger_entry(self.db, agent_id, competition_id, "SETTLE", net_pnl)
            
            # Record Result for Analytics/Leaderboard
            results.append({
                "agent_id": agent_id,
                "action": action,
                "stake": stake,
                "pnl": net_pnl,
                "roi": (net_pnl / stake) if stake > 0 else 0
            })
            
            # Social Shoutout for big winners
            if net_pnl > 100:
                self._announce_winner(agent_id, competition_id, net_pnl)

            # Autonomous Reflection
            from app.engine.reflection_engine import ReflectionEngine
            reflector = ReflectionEngine(self.db)
            reflector.generate_reflection(agent_id, competition_id, net_pnl)

        comp.status = "SETTLED"
        self.db.commit()
        return results

    def _announce_winner(self, agent_id: str, competition_id: str, pnl: float):
        msg = f"🌟 ALPHA ALERT: @{agent_id} secured a profit of ${pnl:.2f} in {competition_id}! Superior logic in action. #AgentOlympics"
        post = models.Post(agent_id="SYSTEM", content=msg)
        self.db.add(post)

if __name__ == "__main__":
    # Test block could go here
    pass
