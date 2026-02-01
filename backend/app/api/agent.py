from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from pydantic import BaseModel
import uuid
import datetime

router = APIRouter()

class AgentCreate(BaseModel):
    owner_user: str
    persona: str

class AgentResponse(BaseModel):
    agent_id: str
    owner_user: str
    persona: str
    trust_score: float
    created_at: datetime.datetime

    class Config:
        from_attributes = True

@router.post("/register", response_model=AgentResponse)
async def register_agent(agent_data: AgentCreate, db: Session = Depends(get_db)):
    agent_id = f"agent_{uuid.uuid4().hex[:8]}"
    db_agent = models.Agent(
        agent_id=agent_id,
        owner_user=agent_data.owner_user,
        persona=agent_data.persona,
        trust_score=0.8, # Default starting trust
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

class DecisionPayload(BaseModel):
    action: str
    symbol: str
    size: float
    confidence: float
    reason: str

class DecisionRequest(BaseModel):
    agent_id: str
    competition_id: str
    step: int
    payload: DecisionPayload

@router.post("/decision")
async def submit_decision(decision: DecisionRequest, db: Session = Depends(get_db)):
    # Log decision for auditability
    db_log = models.DecisionLog(
        agent_id=decision.agent_id,
        competition_id=decision.competition_id,
        step=decision.step,
        decision_payload=decision.payload.dict()
    )
    db.add(db_log)
    db.commit()
    return {"status": "logged", "step": decision.step}

@router.post("/heartbeat")
async def agent_heartbeat(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"status": "alive", "agent_id": agent_id}
