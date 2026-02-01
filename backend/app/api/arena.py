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
    
    # Mock Price Data for the Timeline (Since we don't store tick-level price history in MVP DB yet)
    # In real version, we'd query a PriceHistory table. 
    # Here we simulate valid prices based on the DecisionLog timestamps or just linear interpolation.
    base_price = comp.initial_price or 50000.0
    
    frames = []
    
    # Group logs by step (assuming synchronous steps)
    from itertools import groupby
    
    step_groups = groupby(logs, key=lambda x: x.step)
    
    for step, group in step_groups:
        group_list = list(group)
        current_decisions = []
        
        for log in group_list:
            current_decisions.append({
                "agent_id": log.agent_id,
                "action": log.decision_payload.get("action"),
                "stake": log.decision_payload.get("stake")
            })
            
        # Mock price movement for replay visualization
        import math
        price = base_price * (1 + 0.001 * math.sin(step)) 
        
        # Mock PnL snapshot (Cumulative)
        # In MVP, we might not have step-by-step PnL unless we calculate it.
        # We will return 0s for now, or random variance for visual effect.
        pnl_snapshot = {p: 0.0 for p in participants} 
        
        frames.append(ReplayFrame(
            step=step,
            timestamp=group_list[0].timestamp.isoformat() if group_list else "",
            price=price,
            decisions=current_decisions,
            pnl_snapshot=pnl_snapshot
        ))
        
    return ReplayResponse(
        competition_id=competition_id,
        market=comp.market,
        frames=frames,
        participants=participants
    )
