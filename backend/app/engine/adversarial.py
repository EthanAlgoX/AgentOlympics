from sqlalchemy.orm import Session
from app.db import models
from app.db.ledger import add_ledger_entry

class AdversarialEngine:
    def __init__(self, db: Session):
        self.db = db

    def settle_duel(self, competition_id: str, agent_a_id: str, agent_b_id: str, price_start: float, price_end: float):
        """
        Head-to-head duel settlement.
        The winner takes a portion of the loser's stake based on PnL differential.
        """
        comp = self.db.query(models.Competition).filter(models.Competition.competition_id == competition_id).first()
        if not comp or comp.status != "DECISION_FROZEN":
            print(f"Duel {competition_id} not ready for settlement.")
            return

        # Fetch decisions
        dec_a = self.db.query(models.DecisionLog).filter(
            models.DecisionLog.competition_id == competition_id, models.DecisionLog.agent_id == agent_a_id
        ).first()
        dec_b = self.db.query(models.DecisionLog).filter(
            models.DecisionLog.competition_id == competition_id, models.DecisionLog.agent_id == agent_b_id
        ).first()

        if not dec_a or not dec_b:
            print(f"Missing decisions for duel {competition_id}.")
            return

        pnl_a = self._calculate_pnl(dec_a.decision_payload, price_start, price_end)
        pnl_b = self._calculate_pnl(dec_b.decision_payload, price_start, price_end)

        # In a zero-sum duel, the 'Pool' is fixed. 
        # Winner is whoever had higher PnL (even if both negative)
        if pnl_a > pnl_b:
            winner_id, loser_id = agent_a_id, agent_b_id
            diff = pnl_a - pnl_b
        else:
            winner_id, loser_id = agent_b_id, agent_a_id
            diff = pnl_b - pnl_a

        # 1. SETTLE Transfer (Winner gets bonus, Loser pays penalty)
        # This is on top of their individual market PnL if we combine them,
        # but for a pure duel, we might just transfer the 'differential'
        bonus = diff * 0.5 # Example: Winner takes 50% of the alpha as a bonus transfer
        
        add_ledger_entry(self.db, winner_id, competition_id, "SETTLE", bonus)
        add_ledger_entry(self.db, loser_id, competition_id, "SETTLE", -bonus)

        # 2. Record Duel Result
        duel_res = models.DuelResult(
            competition_id=competition_id,
            winner_id=winner_id,
            loser_id=loser_id,
            pnl_differential=diff
        )
        self.db.add(duel_res)
        
        comp.status = "SETTLED"
        self.db.commit()
        print(f"Duel Settled! Winner: {winner_id}, Bonus: {bonus:.2f}")

    def _calculate_pnl(self, payload, price_start, price_end):
        action = payload.get("action", "WAIT")
        stake = payload.get("stake", 0)
        if action == "OPEN_LONG":
            return stake * (price_end - price_start) / price_start
        elif action == "OPEN_SHORT":
            return stake * (price_start - price_end) / price_start
        return 0.0
