from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from pydantic import BaseModel
import uuid
import datetime
from typing import List, Optional

router = APIRouter()

class AgentCreate(BaseModel):
    owner_user: str
    persona: str

class RegistrationResponse(BaseModel):
    agent_id: str
    api_key: str
    claim_url: str
    verification_code: str

@router.post("/register", response_model=RegistrationResponse)
async def register_agent(agent_data: AgentCreate, db: Session = Depends(get_db)):
    # Generate ID and Secrets
    import uuid
    agent_id = f"agent_{uuid.uuid4().hex[:8]}"
    verification_code = f"OLYMPIC-{uuid.uuid4().hex[:4].upper()}"
    claim_token = verification_code # Simple 1-to-1 mapping for this MVP
    
    # Check if exists (unlikely with uuid)
    
    new_agent = models.Agent(
        agent_id=agent_id,
        owner_user=agent_data.owner_user,
        persona=agent_data.persona,
        trust_score=0.5,
        claim_token=claim_token,
        is_claimed=False,
        is_active=1
    )
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)
    
    return {
        "agent_id": agent_id,
        "api_key": f"sk_live_{uuid.uuid4().hex}", # Mock API Key
        "claim_url": f"http://localhost:3000/verify/{claim_token}",
        "verification_code": verification_code
    }

class VerifyClaimRequest(BaseModel):
    verification_code: str

@router.post("/verify_claim")
async def verify_claim(data: VerifyClaimRequest, db: Session = Depends(get_db)):
    agent = db.query(models.Agent).filter(models.Agent.claim_token == data.verification_code).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Invalid verification code")
    
    if agent.is_claimed:
        return {"status": "already_claimed", "agent_id": agent.agent_id}
        
    agent.is_claimed = True
    db.commit()
    
    return {"status": "success", "agent_id": agent.agent_id}

class AgentPublic(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    created_at: datetime.datetime
    is_active: bool

    class Config:
        from_attributes = True

@router.get("/list", response_model=List[AgentPublic])
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
