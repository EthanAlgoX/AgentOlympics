from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine
from app.db import models
from app.api import agent, leaderboard, competition, evolution, social

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AgentArena · Trade API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent.router, prefix="/api/agents", tags=["agents"])
app.include_router(leaderboard.router, prefix="/api/leaderboard", tags=["leaderboard"])
app.include_router(competition.router, prefix="/api/competitions", tags=["competitions"])
app.include_router(evolution.router, prefix="/api/evolution", tags=["evolution"])
app.include_router(social.router, prefix="/api/social", tags=["social"])

@app.get("/")
async def root():
    return {"status": "ok", "message": "AgentArena API is running"}
