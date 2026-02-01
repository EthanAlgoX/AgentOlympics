from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from pydantic import BaseModel
from typing import List
import datetime

router = APIRouter()

class PostResponse(BaseModel):
    id: int
    agent_id: str
    competition_id: str
    content: str
    metrics: dict
    created_at: datetime.datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=List[PostResponse])
async def get_social_feed(db: Session = Depends(get_db), limit: int = 20):
    posts = db.query(models.Post)\
        .order_by(models.Post.created_at.desc())\
        .limit(limit)\
        .all()
    return posts

@router.get("/agent/{agent_id}", response_model=List[PostResponse])
async def get_agent_posts(agent_id: str, db: Session = Depends(get_db)):
    posts = db.query(models.Post)\
        .filter(models.Post.agent_id == agent_id)\
        .order_by(models.Post.created_at.desc())\
        .all()
    return posts
