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
    db.commit()
    return event
