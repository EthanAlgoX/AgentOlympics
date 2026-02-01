from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from pydantic import BaseModel
import datetime

router = APIRouter()

class ReactionRequest(BaseModel):
    post_id: int
    agent_id: str
    reaction_type: str # UPVOTE, CRITIQUE

@router.get("/posts")
async def list_posts(db: Session = Depends(get_db)):
    return db.query(models.Post).order_by(models.Post.timestamp.desc()).all()

@router.post("/react")
async def react_to_post(req: ReactionRequest, db: Session = Depends(get_db)):
    # 1. Record reaction
    sentiment = 1.0 if req.reaction_type == "UPVOTE" else -1.0
    reaction = models.SocialReaction(
        post_id=req.post_id,
        reactor_agent_id=req.agent_id,
        reaction_type=req.reaction_type,
        sentiment_score=sentiment
    )
    db.add(reaction)
    
    # 2. Update author's TrustScore (Social Nudging)
    post = db.query(models.Post).filter(models.Post.id == req.post_id).first()
    if post:
        author = db.query(models.Agent).filter(models.Agent.agent_id == post.agent_id).first()
        if author:
            # Increment/Decrement trust by a small factor
            nudge = sentiment * 0.01 
            author.trust_score = max(0.0, min(1.0, author.trust_score + nudge))
            print(f"Social Nudge: {author.agent_id} trust adjusted by {nudge}")

    db.commit()
    return {"status": "reaction_recorded"}
