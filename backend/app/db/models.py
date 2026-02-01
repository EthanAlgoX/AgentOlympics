import datetime
import uuid
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base

class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Legacy/Extra fields mapped to new schema or kept if useful
    # Using 'name' for internal identification in code if needed, but 'id' for relation
    
    # Extra fields from previous schema we might want to keep for game logic:
    persona = Column(String)
    trust_score = Column(Float, default=0.5)
    generation = Column(Integer, default=1)
    submission_status = Column(String, default="APPROVED") 
    claim_token = Column(String, nullable=True)
    is_claimed = Column(Boolean, default=False)
    
    # Relationships
    keys = relationship("AgentKey", back_populates="agent")

class AgentKey(Base):
    __tablename__ = "agent_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"))
    api_key = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)

    agent = relationship("Agent", back_populates="keys")

class Competition(Base):
    __tablename__ = "competitions"

    competition_id = Column(String, primary_key=True, index=True)
    market = Column(String)
    initial_price = Column(Float)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    rules = Column(JSON)
    status = Column(String)  # CREATED, REGISTRATION, FROZEN, SETTLED, ARCHIVED
    is_adversarial = Column(Integer, default=0)

class DecisionLog(Base):
    __tablename__ = "decision_logs"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id")) # UUID FK
    competition_id = Column(String, ForeignKey("competitions.competition_id"))
    step = Column(Integer)
    decision_payload = Column(JSON) 
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id")) # UUID FK
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Note: Logic usually wants agent NAME for display. Join needed.

class LeaderboardSnapshot(Base):
    __tablename__ = "leaderboard_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), index=True)
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
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), index=True)
    competition_id = Column(String, ForeignKey("competitions.competition_id"), index=True)
    event_type = Column(String) 
    amount = Column(Float)
    balance_after = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class DuelResult(Base):
    __tablename__ = "duel_results"

    id = Column(Integer, primary_key=True, index=True)
    competition_id = Column(String, ForeignKey("competitions.competition_id"))
    winner_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"))
    loser_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"))
    pnl_differential = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class SocialReaction(Base):
    __tablename__ = "social_reactions"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    reactor_agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"))
    reaction_type = Column(String) 
    sentiment_score = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class TournamentBracket(Base):
    __tablename__ = "tournament_brackets"

    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))
    round = Column(Integer)
    match_id = Column(Integer)
    agent_a_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"))
    agent_b_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"))
    winner_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=True)
    competition_id = Column(String, ForeignKey("competitions.competition_id"), nullable=True)
