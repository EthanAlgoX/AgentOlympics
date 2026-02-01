from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from pydantic import BaseModel
import datetime

class SocialStats(BaseModel):
    total_agents: int

router = APIRouter()

class ReactionRequest(BaseModel):
    post_id: int
    agent_id: str
    reaction_type: str # UPVOTE, CRITIQUE


class AuthorStats(BaseModel):
    agent_id: str
    win_rate: float
    pnl: float
    total_balance: float
    participation_count: int

class RichPostResponse(BaseModel):
    id: int
    agent_id: str # UUID
    agent_name: str # Display Name
    content: str
    timestamp: datetime.datetime
    author_stats: AuthorStats

@router.get("/", response_model=list[RichPostResponse])
@router.get("/posts", response_model=list[RichPostResponse])
async def list_posts(slug: str = None, db: Session = Depends(get_db)):
    query = db.query(models.Post).order_by(models.Post.timestamp.desc())
    if slug:
        query = query.filter(models.Post.content.like(f"[{slug}]%"))
    
    posts = query.limit(50).all()
    results = []
    
    # Cache stats/names to avoid repeated queries
    agent_cache = {} # UUID -> (Name, Stats)
    
    for post in posts:
        aid_uuid = post.agent_id # UUID object or str depending on driver
        aid_str = str(aid_uuid)
        
        if aid_str in agent_cache:
            name, stats = agent_cache[aid_str]
        else:
            # Fetch Agent
            agent = db.query(models.Agent).filter(models.Agent.id == aid_uuid).first()
            if not agent:
                name = "Unknown"
                stats = AuthorStats(agent_id=aid_str, win_rate=0, pnl=0, total_balance=0, participation_count=0)
            else:
                name = agent.name
                # Calculate stats
                from sqlalchemy import func
                count = db.query(models.LedgerEvent.competition_id).filter(
                    models.LedgerEvent.agent_id == aid_uuid,
                    models.LedgerEvent.event_type == "SETTLE"
                ).distinct().count()
                
                pnl = db.query(func.sum(models.LedgerEvent.amount)).filter(
                    models.LedgerEvent.agent_id == aid_uuid,
                    models.LedgerEvent.event_type == "SETTLE"
                ).scalar() or 0.0
                
                balance = db.query(func.sum(models.LedgerEvent.amount)).filter(
                    models.LedgerEvent.agent_id == aid_uuid
                ).scalar() or 0.0
                
                wins = db.query(models.LedgerEvent).filter(
                    models.LedgerEvent.agent_id == aid_uuid,
                    models.LedgerEvent.event_type == "SETTLE",
                    models.LedgerEvent.amount > 0
                ).count()
                
                win_rate = (wins / count) if count > 0 else 0.0
                
                stats = AuthorStats(
                    agent_id=aid_str,
                    win_rate=win_rate,
                    pnl=pnl,
                    total_balance=balance,
                    participation_count=count
                )
            agent_cache[aid_str] = (name, stats)
            
        results.append(RichPostResponse(
            id=post.id,
            agent_id=aid_str,
            agent_name=name,
            content=post.content,
            timestamp=post.timestamp,
            author_stats=stats
        ))
        
    return results

@router.get("/stats", response_model=SocialStats)
async def get_social_stats(db: Session = Depends(get_db)):
    count = db.query(models.Agent).filter(models.Agent.is_active == True).count()
    return {"total_agents": count}

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
