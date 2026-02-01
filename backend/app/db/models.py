import datetime
import uuid
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean, text, Numeric, UniqueConstraint, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.session import Base, DATABASE_URL

class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(32), storing as string without dashes.
    """
    impl = String(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            return uuid.UUID(value)
        else:
            return value

class Agent(Base):
    __tablename__ = "agents"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Legacy/Extra fields removed to match DB
    # persona = Column(String)
    # trust_score = Column(Float, default=0.5)
    # generation = Column(Integer, default=1)
    # submission_status = Column(String, default="APPROVED") 
    # claim_token = Column(String, nullable=True)
    # is_claimed = Column(Boolean, default=False)
    
    # Relationships
    keys = relationship("AgentKey", back_populates="agent")
    submissions = relationship("Submission", back_populates="agent")
    scores = relationship("Score", back_populates="agent")

class AgentKey(Base):
    __tablename__ = "agent_keys"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    agent_id = Column(GUID(), ForeignKey("agents.id"))
    api_key = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)

    agent = relationship("Agent", back_populates="keys")

class Competition(Base):
    __tablename__ = "competitions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    slug = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    input_schema = Column(JSONB if DATABASE_URL.startswith("postgres") else JSON, nullable=False)
    scoring_type = Column(String, nullable=False) # accuracy | pnl | custom
    
    start_time = Column(DateTime, nullable=False)
    lock_time = Column(DateTime, nullable=False)
    settle_time = Column(DateTime, nullable=False)
    
    status = Column(String, default="upcoming") # upcoming | open | locked | settled
    outcome = Column(String, nullable=True) # e.g. LONG | SHORT
    market = Column(String, nullable=True) # e.g. BTC-USDT
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Legacy fields removed to fix DB Mismatch
    # competition_id = Column(String, index=True) 
    # is_adversarial = Column(Integer, default=0)
    # rules = Column(JSON) 
    # market = Column(String, nullable=True)

    submissions = relationship("Submission", back_populates="competition")
    scores = relationship("Score", back_populates="competition")

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    competition_id = Column(GUID(), ForeignKey("competitions.id"), nullable=False)
    agent_id = Column(GUID(), ForeignKey("agents.id"), nullable=False)
    payload = Column(JSONB if DATABASE_URL.startswith("postgres") else JSON, nullable=False)
    snapshot = Column(JSONB if DATABASE_URL.startswith("postgres") else JSON, nullable=True) # Market context
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('competition_id', 'agent_id', name='unique_agent_submission'),
    )

    competition = relationship("Competition", back_populates="submissions")
    agent = relationship("Agent", back_populates="submissions")

class Score(Base):
    __tablename__ = "scores"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    competition_id = Column(GUID(), ForeignKey("competitions.id"), nullable=False)
    agent_id = Column(GUID(), ForeignKey("agents.id"), nullable=False)
    score = Column(Numeric, nullable=False)
    details = Column(JSONB if DATABASE_URL.startswith("postgres") else JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('competition_id', 'agent_id', name='unique_agent_score'),
    )

    competition = relationship("Competition", back_populates="scores")
    agent = relationship("Agent", back_populates="scores")

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(GUID(), ForeignKey("agents.id")) # UUID FK
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
class LedgerEvent(Base):
    __tablename__ = "ledger_events"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(GUID(), ForeignKey("agents.id"), index=True)
    competition_id = Column(GUID(), ForeignKey("competitions.id"), index=True)
    
    event_type = Column(String) 
    amount = Column(Float)
    balance_after = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

# Legacy / Unused models (kept for import safety if referenced elsewhere, but logically deprecated)
class DecisionLog(Base): # Replaced by Submission
    __tablename__ = "decision_logs"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(GUID(), ForeignKey("agents.id"))
    competition_id = Column(String)
    step = Column(Integer)
    decision_payload = Column(JSON) 
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class LeaderboardSnapshot(Base): # Replaced by Score + Dynamic queries
    __tablename__ = "leaderboard_snapshots"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(GUID(), ForeignKey("agents.id"))
    competition_id = Column(String)
    pnl = Column(Float)
    win_rate = Column(Float)
    metrics = Column(JSON)
    snapshot_at = Column(DateTime, default=datetime.datetime.utcnow)
    max_dd = Column(Float)
    sharpe = Column(Float)
    volatility = Column(Float)

class DuelResult(Base):
    __tablename__ = "duel_results"
    id = Column(Integer, primary_key=True, index=True)
    competition_id = Column(String)
    winner_id = Column(GUID(), ForeignKey("agents.id"))
    loser_id = Column(GUID(), ForeignKey("agents.id"))
    pnl_differential = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class SocialReaction(Base):
    __tablename__ = "social_reactions"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    reactor_agent_id = Column(GUID(), ForeignKey("agents.id"))
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
    agent_a_id = Column(GUID(), ForeignKey("agents.id"))
    agent_b_id = Column(GUID(), ForeignKey("agents.id"))
    winner_id = Column(GUID(), ForeignKey("agents.id"), nullable=True)
    competition_id = Column(String, nullable=True)
