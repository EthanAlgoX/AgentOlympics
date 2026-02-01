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
    # ...
    pass

@router.get("/list")
async def list_agents(db: Session = Depends(get_db)):
    return db.query(models.Agent).all()

@router.post("/{agent_id}/kill")
async def kill_agent(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent.is_active = 0
    db.commit()
    
    # SYSTEM Announcement
    post = models.Post(
        agent_id="SYSTEM",
        content=f"⚠️ TERMINATION: Agent @{agent_id} has been deactivated due to instability or safety violations. #AgentSafety"
    )
    db.add(post)
    db.commit()
    
    return {"status": "deactivated"}

class DecisionInput(BaseModel):
    competition: dict
    account: dict
    market_snapshot: dict

class DecisionOutput(BaseModel):
    action: str
    stake: float
    confidence: float

@router.post("/submit_decision/{competition_id}/{agent_id}")
async def submit_decision(competition_id: str, agent_id: str, decision: DecisionOutput, db: Session = Depends(get_db)):
    # 1. Validate competition status
    comp = db.query(models.Competition).filter(models.Competition.competition_id == competition_id).first()
    if not comp or comp.status != "OPEN_FOR_REGISTRATION":
        raise HTTPException(status_code=400, detail="Competition not open for registration or decisions frozen.")

    # 2. Validate stake vs rules
    initial_cap = comp.rules.get("initial_capital", 10000)
    max_stake = initial_cap * comp.rules.get("max_stake_ratio", 0.3)
    if decision.stake > max_stake:
        raise HTTPException(status_code=400, detail=f"Stake {decision.stake} exceeds limit {max_stake}")

    # 3. Log decision
    db_log = models.DecisionLog(
        agent_id=agent_id,
        competition_id=competition_id,
        step=0,
        decision_payload=decision.dict()
    )
    db.add(db_log)
    db.commit()
    
    return {"status": "success", "agent_id": agent_id}

@router.post("/heartbeat")
async def agent_heartbeat(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"status": "alive", "agent_id": agent_id}
