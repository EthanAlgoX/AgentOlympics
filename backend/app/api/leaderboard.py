from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from pydantic import BaseModel
from typing import List
from app.db.ledger import calculate_advanced_metrics
import datetime

router = APIRouter()

class RankingResponse(BaseModel):
    agent_id: str
    pnl: float
    sharpe: float
    max_dd: float
    trust_score: float

    class Config:
        from_attributes = True

class LeaderboardResponse(BaseModel):
    competition_id: str
    snapshot_at: datetime.datetime
    rankings: List[RankingResponse]

@router.get("/{competition_id}", response_model=LeaderboardResponse)
async def get_leaderboard(competition_id: str, db: Session = Depends(get_db)):
    snapshots = db.query(models.LeaderboardSnapshot)\
        .filter(models.LeaderboardSnapshot.competition_id == competition_id)\
        .order_by(models.LeaderboardSnapshot.pnl.desc())\
        .all()
    
    # If no snapshots, return empty list
    last_snapshot_at = snapshots[0].snapshot_at if snapshots else datetime.datetime.utcnow()
    
    return {
        "competition_id": competition_id,
        "snapshot_at": last_snapshot_at,
        "rankings": snapshots
    }

@router.get("/agents/{agent_id}")
async def get_agent_stats(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()
    if not agent:
        return {"error": "Agent not found"}
    
    competitions = db.query(models.AgentAccount).filter(models.AgentAccount.agent_id == agent_id).all()
    
    return {
        "agent": agent,
        "ongoing_competitions": len(competitions)
    }

@router.get("/global/ranking")
async def get_global_leaderboard(db: Session = Depends(get_db)):
    from sqlalchemy import func
    
    # Simple aggregation of PnL from ledger events
    results = db.query(
        models.LedgerEvent.agent_id,
        func.sum(models.LedgerEvent.amount).label("total_pnl"),
        func.count(models.LedgerEvent.id).label("total_events")
    ).filter(models.LedgerEvent.event_type == "SETTLE").group_by(models.LedgerEvent.agent_id).all()
    
    leaderboard = []
    for r in results:
        # Calculate win rate (amount > 0)
        wins = db.query(models.LedgerEvent).filter(
            models.LedgerEvent.agent_id == r.agent_id,
            models.LedgerEvent.event_type == "SETTLE",
            models.LedgerEvent.amount > 0
        ).count()
        
        win_rate = wins / r.total_events if r.total_events > 0 else 0
        
        advanced = calculate_advanced_metrics(db, r.agent_id)
        
        leaderboard.append({
            "agent_id": r.agent_id,
            "pnl": r.total_pnl,
            "win_rate": win_rate,
            "competitions": r.total_events,
            "sharpe": advanced["sharpe"],
            "max_dd": advanced["max_dd"],
            "volatility": advanced["volatility"],
            "trust_score": 0.8
        })
    
    return sorted(leaderboard, key=lambda x: x["pnl"], reverse=True)
