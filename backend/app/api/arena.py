from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter()

class ReplayFrame(BaseModel):
    step: int
    timestamp: str
    price: float
    decisions: List[Dict[str, Any]] # Agent actions this step
    pnl_snapshot: Dict[str, float] # Agent PnL at this step

class ReplayResponse(BaseModel):
    competition_id: str
    market: str
    description: str = "No description provided."
    rules: Dict[str, Any] = {}
    prize_pool: str = "10,000 USD"
    frames: List[ReplayFrame]
    participants: List[str]

@router.get("/{competition_id}/replay", response_model=ReplayResponse)
async def get_competition_replay(competition_id: str, db: Session = Depends(get_db)):
    comp = db.query(models.Competition).filter(models.Competition.competition_id == competition_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competition not found")
        
    # Fetch all decisions
    logs = db.query(models.DecisionLog).filter(models.DecisionLog.competition_id == competition_id).order_by(models.DecisionLog.step).all()
    
    # Identify participants
    participants = list(set([log.agent_id for log in logs]))
    
    # Mock Price Data for the Timeline
    base_price = comp.initial_price or 50000.0
    
    frames = []
    
    # Group logs by step
    from itertools import groupby
    
    step_groups = groupby(logs, key=lambda x: x.step)
    
    for step, group in step_groups:
        group_list = list(group)
        current_decisions = []
        
        for log in group_list:
            current_decisions.append({
                "agent_id": log.agent_id,
                "action": log.decision_payload.get("action"),
                "stake": log.decision_payload.get("stake"),
                "thought": log.decision_payload.get("thought", "No thought provided."),
                "confidence": log.decision_payload.get("confidence", 0.0)
            })
            
        # Mock price movement for replay visualization
        import math
        price = base_price * (1 + 0.001 * math.sin(step)) 
        
        # Mock PnL snapshot 
        pnl_snapshot = {p: 0.0 for p in participants} 
        
        frames.append(ReplayFrame(
            step=step,
            timestamp=group_list[0].timestamp.isoformat() if group_list else "",
            price=price,
            decisions=current_decisions,
            pnl_snapshot=pnl_snapshot
        ))
    
    # Extract description and prize from rules if available
    rules = comp.rules or {}
    description = rules.get("description", f"Trading competition on {comp.market}.")
    prize_pool = rules.get("prize_pool", "10,000 USD")

    return ReplayResponse(
        competition_id=competition_id,
        market=comp.market,
        description=description,
        rules=rules,
        prize_pool=prize_pool,
        frames=frames,
        participants=participants
    )
