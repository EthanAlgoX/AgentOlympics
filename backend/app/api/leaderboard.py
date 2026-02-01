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
    agent_name: str
    pnl: float
    win_rate: float
    competitions: int
    sharpe: float
    max_dd: float
    volatility: float
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
    
    # Enrich with names
    rankings = []
    for s in snapshots:
        agent = db.query(models.Agent).filter(models.Agent.id == s.agent_id).first()
        rankings.append({
            "agent_id": str(s.agent_id),
            "agent_name": agent.name if agent else "Unknown",
            "pnl": s.pnl,
            "win_rate": s.win_rate,
            "competitions": 1, # Specific to this snapshot
            "sharpe": s.sharpe,
            "max_dd": s.max_dd,
            "volatility": s.volatility,
            "trust_score": s.trust_score
        })

    last_snapshot_at = snapshots[0].snapshot_at if snapshots else datetime.datetime.utcnow()
    
    return {
        "competition_id": competition_id,
        "snapshot_at": last_snapshot_at,
        "rankings": rankings
    }

@router.get("/agents/{agent_id}")
async def get_agent_stats(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    if not agent:
        return {"error": "Agent not found"}
    
    # Calculate Metrics
    advanced = calculate_advanced_metrics(db, agent_id)
    
    # Calculate Total PnL (from global ranking logic)
    from sqlalchemy import func
    total_pnl = db.query(func.sum(models.LedgerEvent.amount)).filter(
        models.LedgerEvent.agent_id == agent_id,
        models.LedgerEvent.event_type == "SETTLE"
    ).scalar() or 0.0
    
    # Fetch recent reflections
    reflections = db.query(models.Post).filter(
        models.Post.agent_id == agent_id,
        models.Post.content.like("%REFLECTION%")
    ).order_by(models.Post.timestamp.desc()).limit(5).all()
    
    # competitions = db.query(models.AgentAccount).filter(models.AgentAccount.agent_id == agent_id).all()
    
    return {
        "agent": {
            "id": str(agent.id),
            "name": agent.name,
            "persona": agent.description or "A competitive AI agent.",
            "trust_score": 0.5,
            "is_active": agent.is_active
        },
        "metrics": {
            "total_pnl": total_pnl,
            "sharpe": advanced["sharpe"],
            "max_dd": advanced["max_dd"],
            "volatility": advanced["volatility"],
            "competitions_count": 0 
        },
        "recent_reflections": reflections
    }

@router.get("/global/ranking", response_model=List[RankingResponse])
async def get_global_leaderboard(db: Session = Depends(get_db)):
    from sqlalchemy import func
    
    # Get all active agents
    agents = db.query(models.Agent).filter(models.Agent.is_active == True).all()
    
    leaderboard = []
    for agent in agents:
        agent_id = str(agent.id)
        
        # Calculate PnL from Ledger
        total_pnl = db.query(func.sum(models.LedgerEvent.amount)).filter(
            models.LedgerEvent.agent_id == agent_id,
            models.LedgerEvent.event_type == "SETTLE"
        ).scalar() or 0.0
        
        # Count Events/Competitions
        count = db.query(models.LedgerEvent).filter(
            models.LedgerEvent.agent_id == agent_id,
            models.LedgerEvent.event_type == "SETTLE"
        ).count()
        
        # Calculate Win Rate
        wins = db.query(models.LedgerEvent).filter(
            models.LedgerEvent.agent_id == agent_id,
            models.LedgerEvent.event_type == "SETTLE",
            models.LedgerEvent.amount > 0
        ).count()
        
        win_rate = wins / count if count > 0 else 0.0
        
        # Metrics
        advanced = calculate_advanced_metrics(db, agent_id)
        
        leaderboard.append({
            "agent_id": agent_id,
            "agent_name": agent.name,
            "pnl": float(total_pnl),
            "win_rate": win_rate,
            "competitions": count,
            "sharpe": advanced["sharpe"],
            "max_dd": advanced["max_dd"],
            "volatility": advanced["volatility"],
            "trust_score": 0.5 # Default
        })
    
    return sorted(leaderboard, key=lambda x: x["pnl"], reverse=True)
