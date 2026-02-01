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

@router.get("/list")
async def list_competitions(db: Session = Depends(get_db)):
    comps = db.query(models.Competition).all()
    results = []
    for c in comps:
        # Default prize if not in description (schema change: rules removed)
        # Parse description or default
        prize = "1,000 USD" # Default for now
        
        # Count participants (submissions)
        part_count = db.query(models.Submission).filter(models.Submission.competition_id == c.id).count()
        
        results.append({
            "id": c.slug, # Use slug as ID for frontend routing
            "title": c.title,
            "status": c.status,
            "pool": prize,
            "participants": part_count,
            "market": c.market or "Unknown"
        })
    return results

@router.get("/{competition_id}/replay", response_model=ReplayResponse)
async def get_competition_replay(competition_id: str, db: Session = Depends(get_db)):
    # competition_id here is the slug from frontend
    comp = db.query(models.Competition).filter(models.Competition.slug == competition_id).first()
    if not comp:
        # Fallback check if it was a GUID (unlikely but safe)
        try:
            import uuid
            uid = uuid.UUID(competition_id)
            comp = db.query(models.Competition).filter(models.Competition.id == uid).first()
        except:
            pass
            
    if not comp:
        raise HTTPException(status_code=404, detail="Competition not found")
        
    # Fetch all submissions (decisions)
    subs = db.query(models.Submission).filter(models.Submission.competition_id == comp.id).order_by(models.Submission.submitted_at).all()
    
    # Identify participants
    # We need agent names, so we might want to join or fetch
    participants = []
    
    current_decisions = []
    
    for sub in subs:
        agent = db.query(models.Agent).filter(models.Agent.id == sub.agent_id).first()
        agent_name = agent.name if agent else str(sub.agent_id)
        if agent_name not in participants:
            participants.append(agent_name)
            
        payload = sub.payload or {}
        current_decisions.append({
            "agent_id": agent_name,
            "action": payload.get("action", "HOLD"),
            "stake": payload.get("stake", 0.0),
            "thought": payload.get("thought", "Signal received."),
            "confidence": payload.get("confidence", 0.0)
        })
            
    # Mock Price Data for the Timeline based on settle time / start time
    base_price = 50000.0 # Placeholder
    
    frames = []
    
    # 1 Step Frame consisting of all decisions (since it's a 1-shot comp now)
    # We can fake a "Step 1"
    
    pnl_snapshot = {p: 0.0 for p in participants} 
    
    frames.append(ReplayFrame(
        step=1,
        timestamp=comp.settle_time.isoformat() if comp.settle_time else "",
        price=base_price,
        decisions=current_decisions,
        pnl_snapshot=pnl_snapshot
    ))
    
    return ReplayResponse(
        competition_id=comp.slug,
        market=comp.market or "Unknown",
        description=comp.description or comp.title,
        rules={}, # No rules content stored anymore
        prize_pool="1,000 USD",
        frames=frames,
        participants=participants
    )
