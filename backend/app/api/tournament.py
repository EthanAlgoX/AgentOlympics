from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from pydantic import BaseModel
from typing import List, Optional
import datetime

router = APIRouter()

class BracketSchema(BaseModel):
    round: int
    agent_a_id: str
    agent_b_id: str
    winner_id: Optional[str] = None
    competition_id: Optional[str] = None

@router.get("/{tournament_id}/brackets")
async def get_brackets(tournament_id: int, db: Session = Depends(get_db)):
    return db.query(models.TournamentBracket).filter(models.TournamentBracket.tournament_id == tournament_id).all()

@router.post("/create")
async def create_tournament(name: str, db: Session = Depends(get_db)):
    tournament = models.Tournament(name=name, status="SCHEDULED")
    db.add(tournament)
    db.commit()
    db.refresh(tournament)
    return tournament
