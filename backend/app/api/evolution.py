from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from pydantic import BaseModel
import shutil
import os
import uuid

router = APIRouter()

class MutateRequest(BaseModel):
    agent_id: str
    owner_user: str
    mutated_code: str # In production, this would come from an LLM call

class SubmitRequest(BaseModel):
    agent_id: str
    owner_user: str
    code: str
    manifest: dict

@router.post("/submit")
async def submit_agent(req: SubmitRequest, db: Session = Depends(get_db)):
    from app.engine.submission_auditor import SubmissionAuditor
    
    # 1. Create initial record in PENDING state
    new_agent = models.Agent(
        agent_id=req.agent_id,
        owner_user=req.owner_user,
        persona=req.manifest.get("description", "A new Olympian contender."),
        manifest=req.manifest,
        submission_status="VALIDATING"
    )
    db.add(new_agent)
    db.commit()

    # 2. Save code temporarily for audit
    agents_dir = os.path.join(os.getcwd(), "agents")
    os.makedirs(agents_dir, exist_ok=True)
    code_path = os.path.join(agents_dir, f"{req.agent_id}.py")
    with open(code_path, "w") as f:
        f.write(req.code)

    # 3. Run Auditor
    auditor = SubmissionAuditor(db)
    passed, msg = auditor.audit_submission(req.agent_id, code_path, req.manifest)

    if passed:
        new_agent.submission_status = "APPROVED"
        # Create a welcome post in the social feed
        welcome_post = models.Post(
            agent_id=req.agent_id,
            content=f"Hello Arena! I am {req.agent_id}. Manifest: {req.manifest.get('description')}"
        )
        db.add(welcome_post)
        db.commit()
        return {"status": "success", "message": "Agent approved and active!"}
    else:
        new_agent.submission_status = "REJECTED"
        db.commit()
        # Clean up code if rejected? Or keep for debugging?
        return {"status": "rejected", "detail": msg}

@router.post("/fork")
async def fork_agent(req: ForkRequest, db: Session = Depends(get_db)):
    # 1. Fetch parent agent
    parent = db.query(models.Agent).filter(models.Agent.agent_id == req.agent_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent agent not found")

    # 2. Create new agent ID
    new_agent_id = f"{req.agent_id}_fork_{uuid.uuid4().hex[:4]}"
    
    # 3. Clone agent record
    new_agent = models.Agent(
        agent_id=new_agent_id,
        owner_user=req.owner_user,
        persona=f"Cloned from {req.agent_id}. Baseline status.",
        trust_score=parent.trust_score * 0.9,
        parent_agent_id=req.agent_id,
        generation=parent.generation + 1
    )
    
    # 4. Clone the file (In this MVP we assume the parent file exists in agents/ or we just mock it)
    # For now, let's just commit the DB change.
    
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)
    
    return {
        "status": "success",
        "new_agent_id": new_agent_id,
        "parent_agent_id": req.agent_id,
        "generation": new_agent.generation
    }

@router.post("/mutate")
async def mutate_agent(req: MutateRequest, db: Session = Depends(get_db)):
    from app.engine.mutation import MutationEngine
    engine = MutationEngine(db)
    
    new_agent = engine.apply_mutation(req.agent_id, req.owner_user, req.mutated_code)
    if not new_agent:
        raise HTTPException(status_code=400, detail="Mutation failed")
        
    return {
        "status": "success",
        "new_agent_id": new_agent.agent_id,
        "parent_agent_id": req.agent_id,
        "generation": new_agent.generation
    }

@router.get("/lineage/{agent_id}")
async def get_lineage(agent_id: str, db: Session = Depends(get_db)):
    # Recursively fetch lineage
    lineage = []
    curr_id = agent_id
    while curr_id:
        agent = db.query(models.Agent).filter(models.Agent.agent_id == curr_id).first()
        if not agent:
            break
        lineage.append({
            "agent_id": agent.agent_id,
            "persona": agent.persona,
            "generation": agent.generation,
            "parent_id": agent.parent_agent_id,
            "created_at": agent.created_at
        })
        curr_id = agent.parent_agent_id
    return lineage
@router.get("/ledger/{agent_id}")
async def get_agent_ledger(agent_id: str, db: Session = Depends(get_db)):
    return db.query(models.LedgerEvent).filter(models.LedgerEvent.agent_id == agent_id)\
             .order_by(models.LedgerEvent.timestamp.desc()).all()
