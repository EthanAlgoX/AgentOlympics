from sqlalchemy.orm import Session
from app.db import models
from app.db.ledger import add_ledger_entry, get_agent_balance
import datetime

class SettlementEngine:
    def __init__(self, db: Session):
        self.db = db

    def settle_competition(self, competition_id: str, price_start: float, price_end: float):
        """
        Deterministic settlement according to formal formula.
        """
        comp = self.db.query(models.Competition).filter(models.Competition.competition_id == competition_id).first()
        if not comp or comp.status != "DECISION_FROZEN":
            print(f"Competition {competition_id} not ready for settlement.")
            return

        # Fetch all decision logs for this competition
        decisions = self.db.query(models.DecisionLog).filter(models.DecisionLog.competition_id == competition_id).all()
        
        for decision in decisions:
            payload = decision.decision_payload
            agent_id = decision.agent_id
            action = payload.get("action", "WAIT")
            stake = payload.get("stake", 0)
            
            pnl = 0.0
            if action == "OPEN_LONG":
                pnl = stake * (price_end - price_start) / price_start
            elif action == "OPEN_SHORT":
                pnl = stake * (price_start - price_end) / price_start
            
            # 1. SETTLE event (PnL)
            add_ledger_entry(self.db, agent_id, competition_id, "SETTLE", pnl)
            
            # 2. FEE event (on stake)
            fee_rate = comp.rules.get("fee_rate", 0.0005)
            fee = stake * fee_rate
            add_ledger_entry(self.db, agent_id, competition_id, "FEE", -fee)
            
            print(f"Agent {agent_id} settled. PnL: {pnl:.2f}, Fee: {fee:.2f}")

        comp.status = "SETTLED"
        self.db.commit()
        print(f"Competition {competition_id} settled successfully.")
