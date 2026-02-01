import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from app.db.session import Base

class Agent(Base):
    __tablename__ = "agents"

    agent_id = Column(String, primary_key=True, index=True)
    owner_user = Column(String)
    persona = Column(String)
    trust_score = Column(Float, default=0.5)
    parent_agent_id = Column(String, ForeignKey("agents.agent_id"), nullable=True)
    generation = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Competition(Base):
    __tablename__ = "competitions"

    competition_id = Column(String, primary_key=True, index=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    rules = Column(JSON)
    status = Column(String)  # CREATED, REGISTRATION, FROZEN, SETTLED, ARCHIVED
    is_adversarial = Column(Integer, default=0)

class DecisionLog(Base):
    __tablename__ = "decision_logs"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, ForeignKey("agents.agent_id"))
    competition_id = Column(String, ForeignKey("competitions.competition_id"))
    decision_payload = Column(JSON) # e.g. {"action": "OPEN_LONG", "stake": 100}
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, ForeignKey("agents.agent_id"))
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class LeaderboardSnapshot(Base):
    __tablename__ = "leaderboard_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, ForeignKey("agents.agent_id"), index=True)
    competition_id = Column(String, ForeignKey("competitions.competition_id"), index=True)
    pnl = Column(Float)
    win_rate = Column(Float)
    max_dd = Column(Float)
    sharpe = Column(Float)
    volatility = Column(Float)
    metrics = Column(JSON)
    snapshot_at = Column(DateTime, default=datetime.datetime.utcnow)

class LedgerEvent(Base):
    __tablename__ = "ledger_events"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, ForeignKey("agents.agent_id"), index=True)
    competition_id = Column(String, ForeignKey("competitions.competition_id"), index=True)
    event_type = Column(String) # LOCK, UNLOCK, SETTLE, FEE
    amount = Column(Float)
    balance_after = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class DuelResult(Base):
    __tablename__ = "duel_results"

    id = Column(Integer, primary_key=True, index=True)
    competition_id = Column(String, ForeignKey("competitions.competition_id"))
    winner_id = Column(String, ForeignKey("agents.agent_id"))
    loser_id = Column(String, ForeignKey("agents.agent_id"))
    pnl_differential = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class SocialReaction(Base):
    __tablename__ = "social_reactions"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    reactor_agent_id = Column(String, ForeignKey("agents.agent_id"))
    reaction_type = Column(String) # UPVOTE, CRITIQUE
    sentiment_score = Column(Float) # 1.0 for upvote, -1.0 for critique
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
