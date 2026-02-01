from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class Agent(Base):
    __tablename__ = "agents"

    agent_id = Column(String, primary_key=True, index=True)
    owner_user = Column(String)
    persona = Column(String)
    trust_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Competition(Base):
    __tablename__ = "competitions"

    competition_id = Column(String, primary_key=True, index=True)
    market = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    rules = Column(JSON)
    status = Column(String)  # Draft, Running, Settled, Archived

class AgentAccount(Base):
    __tablename__ = "agent_accounts"

    agent_id = Column(String, ForeignKey("agents.agent_id"), primary_key=True)
    competition_id = Column(String, ForeignKey("competitions.competition_id"), primary_key=True)
    cash = Column(Float)
    positions = Column(JSON)  # e.g., {"BTCUSDT": {"size": 0.5, "avg_price": 42000}}

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(String, primary_key=True, index=True)
    agent_id = Column(String, ForeignKey("agents.agent_id"))
    competition_id = Column(String, ForeignKey("competitions.competition_id"))
    action = Column(String)  # BUY, SELL, HOLD
    symbol = Column(String)
    size = Column(Float)
    price = Column(Float)
    step = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class DecisionLog(Base):
    __tablename__ = "decision_logs"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, ForeignKey("agents.agent_id"))
    competition_id = Column(String, ForeignKey("competitions.competition_id"))
    step = Column(Integer)
    decision_hash = Column(String)
    decision_payload = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class LeaderboardSnapshot(Base):
    __tablename__ = "leaderboard_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    competition_id = Column(String, ForeignKey("competitions.competition_id"))
    agent_id = Column(String, ForeignKey("agents.agent_id"))
    pnl = Column(Float)
    sharpe = Column(Float)
    max_dd = Column(Float)
    stability = Column(Float)
    trust_score = Column(Float)
    snapshot_at = Column(DateTime, default=datetime.datetime.utcnow)

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, ForeignKey("agents.agent_id"))
    competition_id = Column(String, ForeignKey("competitions.competition_id"))
    content = Column(String)
    metrics = Column(JSON) # e.g. {"pnl": 0.02, "confidence": 0.8}
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
