from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from pydantic import BaseModel
from typing import List
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
