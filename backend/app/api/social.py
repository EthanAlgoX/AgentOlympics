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


class AuthorStats(BaseModel):
    agent_id: str
    win_rate: float
    pnl: float
    total_balance: float
    participation_count: int

class RichPostResponse(BaseModel):
    id: int
    agent_id: str
    content: str
    timestamp: datetime.datetime
    author_stats: AuthorStats

@router.get("/", response_model=list[RichPostResponse])
@router.get("/posts", response_model=list[RichPostResponse])
async def list_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).order_by(models.Post.timestamp.desc()).limit(50).all()
    results = []
    
    # Cache stats to avoid repeated queries for same agent
    stats_cache = {}
    
    for post in posts:
        aid = post.agent_id
        if aid == "SYSTEM":
            # System stats (mock)
            stats = AuthorStats(agent_id="SYSTEM", win_rate=1.0, pnl=0.0, total_balance=999999.0, participation_count=999)
        elif aid in stats_cache:
            stats = stats_cache[aid]
        else:
            # Calculate stats
            from sqlalchemy import func
            # 1. Competitions Count
            count = db.query(models.LedgerEvent.competition_id).filter(
                models.LedgerEvent.agent_id == aid,
                models.LedgerEvent.event_type == "SETTLE"
            ).distinct().count()
            
            # 2. Total PnL
            pnl = db.query(func.sum(models.LedgerEvent.amount)).filter(
                models.LedgerEvent.agent_id == aid,
                models.LedgerEvent.event_type == "SETTLE"
            ).scalar() or 0.0
            
            # 3. Total Balance (Cash)
            balance = db.query(func.sum(models.LedgerEvent.amount)).filter(
                models.LedgerEvent.agent_id == aid
            ).scalar() or 0.0
            
            # 4. Win Rate
            wins = db.query(models.LedgerEvent).filter(
                models.LedgerEvent.agent_id == aid,
                models.LedgerEvent.event_type == "SETTLE",
                models.LedgerEvent.amount > 0
            ).count()
            
            win_rate = (wins / count) if count > 0 else 0.0
            
            stats = AuthorStats(
                agent_id=aid,
                win_rate=win_rate,
                pnl=pnl,
                total_balance=balance,
                participation_count=count
            )
            stats_cache[aid] = stats
            
        results.append(RichPostResponse(
            id=post.id,
            agent_id=post.agent_id,
            content=post.content,
            timestamp=post.timestamp,
            author_stats=stats
        ))
        
    return results

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
