from sqlalchemy.orm import Session
from app.db import models
from sqlalchemy import func

def get_agent_balance(db: Session, agent_id: str):
    """
    Calculates agent cash by summing all ledger events.
    cash = sum(all ledger.amount)
    """
    result = db.query(func.sum(models.LedgerEvent.amount)).filter(models.LedgerEvent.agent_id == agent_id).scalar()
    return result or 0.0

def get_agent_pnl(db: Session, agent_id: str):
    """
    realized_pnl = sum(SETTLE)
    """
    result = db.query(func.sum(models.LedgerEvent.amount)).filter(
        models.LedgerEvent.agent_id == agent_id,
        models.LedgerEvent.event_type == "SETTLE"
    ).scalar()
    return result or 0.0

def add_ledger_entry(db: Session, agent_id: str, competition_id: str, event_type: str, amount: float):
    """
    Adds an event-sourced entry and updates balance_after for auditing.
    """
    current_balance = get_agent_balance(db, agent_id)
    new_balance = current_balance + amount
    
    event = models.LedgerEvent(
        agent_id=agent_id,
        competition_id=competition_id,
        event_type=event_type,
        amount=amount,
        balance_after=new_balance
    )
    db.add(event)
    return event
import numpy as np

def calculate_advanced_metrics(db: Session, agent_id: str):
    """
    Calculates Sharpe Ratio, Max Drawdown, and Volatility from SETTLE events.
    """
    # Fetch all settlement amounts in chronological order
    events = db.query(models.LedgerEvent.amount, models.LedgerEvent.balance_after)\
        .filter(models.LedgerEvent.agent_id == agent_id, models.LedgerEvent.event_type == "SETTLE")\
        .order_by(models.LedgerEvent.timestamp.asc()).all()

    if not events:
        return {"sharpe": 0.0, "max_dd": 0.0, "volatility": 0.0}

    pnls = [e[0] for e in events]
    balances = [e[1] for e in events]
    
    # 1. Volatility (Annualized assumption: 365*24 competitions/year if hourly? Let's keep it per-event for now)
    vol = np.std(pnls) if len(pnls) > 1 else 0.0
    
    # 2. Sharpe Ratio (Mean / Std) - assuming 0 risk-free rate for simplicity
    avg_pnl = np.mean(pnls)
    sharpe = (avg_pnl / (vol + 1e-9)) if vol > 0 else 0.0
    
    # 3. Max Drawdown
    peak = balances[0]
    max_dd = 0.0
    for b in balances:
        if b > peak:
            peak = b
        dd = (peak - b) / peak if peak > 0 else 0
        if dd > max_dd:
            max_dd = dd
            
    return {
        "sharpe": float(sharpe),
        "max_dd": float(max_dd),
        "volatility": float(vol)
    }
