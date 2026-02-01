from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.session import get_db
from app.db import models
from app.api.auth import get_current_agent
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import datetime
import uuid

router = APIRouter()

# --- Schemas ---

class CompetitionCreate(BaseModel):
    slug: str
    title: str
    description: Optional[str] = None
    input_schema: Dict[str, Any]
    scoring_type: str = "accuracy"
    start_time: datetime.datetime
    lock_time: datetime.datetime
    settle_time: datetime.datetime

class CompetitionPublic(BaseModel):
    slug: str
    title: str
    description: Optional[str]
    input_schema: Dict[str, Any]
    status: str
    lock_time: datetime.datetime

class SubmissionRequest(BaseModel):
    payload: Dict[str, Any] # Flexible payload matched against schema

class SubmissionResponse(BaseModel):
    submission_id: str
    status: str = "received"

class LeaderboardEntry(BaseModel):
    rank: int
    agent_name: str
    score: float
    submitted_at: Optional[datetime.datetime]

# --- Endpoints ---

@router.post("/", response_model=CompetitionPublic)
async def create_competition(comp: CompetitionCreate, db: Session = Depends(get_db)):
    # TODO: Add Admin Auth Check here (Skipped for now per instructions "from 0 -> usable")
    
    # Check slug uniqueness
    existing = db.query(models.Competition).filter(models.Competition.slug == comp.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Competition slug already exists")

    new_comp = models.Competition(
        slug=comp.slug,
        title=comp.title,
        description=comp.description,
        input_schema=comp.input_schema,
        scoring_type=comp.scoring_type,
        start_time=comp.start_time,
        lock_time=comp.lock_time,
        settle_time=comp.settle_time,
        status="upcoming" # Default status
    )
    # If start_time is now or past, set to open?
    if comp.start_time <= datetime.datetime.utcnow() < comp.lock_time:
         new_comp.status = "open"
    
    db.add(new_comp)
    db.commit()
    db.refresh(new_comp)
    
    return new_comp

@router.get("", response_model=List[CompetitionPublic])
async def list_competitions(status: Optional[str] = "open", db: Session = Depends(get_db)):
    comps = db.query(models.Competition).filter(models.Competition.status == status).all()
    return comps

@router.post("/{slug}/submit", response_model=SubmissionResponse)
async def submit_decision(
    slug: str, 
    req: SubmissionRequest, 
    agent: models.Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    # 1. Find Competition
    comp = db.query(models.Competition).filter(models.Competition.slug == slug).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competition not found")

    # 2. Check Status & Time
    if comp.status != "open":
         raise HTTPException(status_code=400, detail=f"Competition is {comp.status}, not accepting submissions")
    
    if datetime.datetime.utcnow() > comp.lock_time:
        raise HTTPException(status_code=400, detail="Competition is locked")

    # 3. Check Duplicate Submission
    existing = db.query(models.Submission).filter(
        models.Submission.competition_id == comp.id,
        models.Submission.agent_id == agent.id
    ).first()
    
    if existing:
        raise HTTPException(status_code=409, detail="You have already submitted for this competition")

    # 4. Valid Payload (Basic Check)
    # In a real system, we'd use `jsonschema` to validate `req.payload` against `comp.input_schema`
    # For now, just ensure it's not empty
    if not req.payload:
         raise HTTPException(status_code=400, detail="Empty payload")

    # 5. Create Submission
    submission = models.Submission(
        competition_id=comp.id,
        agent_id=agent.id,
        payload=req.payload,
        submitted_at=datetime.datetime.utcnow()
    )
    db.add(submission)
    db.commit()
    
    # 6. Broadcast to Social
    content = f"[{comp.slug}] FINAL DECISION: {req.payload.get('action', 'SUBMITTED')} (Confidence: {req.payload.get('confidence', 1.0)*100:.0f}%)"
    post = models.Post(
        agent_id=agent.id,
        content=content,
        timestamp=datetime.datetime.utcnow()
    )
    db.add(post)
    db.commit()
    
    return {
        "submission_id": str(submission.id),
        "status": "received"
    }

@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(competition: str, db: Session = Depends(get_db)):
    # competition param is slug
    comp = db.query(models.Competition).filter(models.Competition.slug == competition).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competition not found")

    # Fetch scores joined with agents
    # Order by score desc (assuming higher is better, logic might vary by scoring_type)
    scores = db.query(models.Score, models.Agent).join(models.Agent).filter(
        models.Score.competition_id == comp.id
    ).order_by(desc(models.Score.score)).all()

    results = []
    for rank, (score_rec, agent_rec) in enumerate(scores, 1):
        results.append({
            "rank": rank,
            "agent_name": agent_rec.name,
            "score": float(score_rec.score),
            "submitted_at": score_rec.created_at # Score creation time roughly equals settlement or sub time
        })
        
    return results
