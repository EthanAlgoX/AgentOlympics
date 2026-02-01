from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine, DATABASE_URL
from app.db import models
from app.api import agent, leaderboard, evolution, social, tournament, arena, auth, competitions

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AgentOlympics · Trade API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent.router, prefix="/api/agents", tags=["agents"])
app.include_router(auth.router, prefix="/api/v1/agents", tags=["auth"])
app.include_router(competitions.router, prefix="/api/v1/competitions", tags=["competitions"])
app.include_router(leaderboard.router, prefix="/api/leaderboard", tags=["leaderboard"])
app.include_router(evolution.router, prefix="/api/evolution", tags=["evolution"])
app.include_router(social.router, prefix="/api/social", tags=["social"])
app.include_router(arena.router, prefix="/api/arena", tags=["arena"])
app.include_router(tournament.router, prefix="/api/tournament", tags=["tournament"])

import asyncio
from app.engine.scheduler import CompetitionScheduler

@app.on_event("startup")
async def start_services():
    # 1. Verify Database Connection
    try:
        masked_url = str(DATABASE_URL)
        if "://" in masked_url:
            masked_url = masked_url.split("://")[0] + "://...@" + masked_url.split("@")[-1] if "@" in masked_url else masked_url[:15] + "..."
        print(f"DB Config: {masked_url}")
        
        with engine.connect() as connection:
            print("DB connected")
    except Exception as e:
        print(f"DB Connection FAILED: {e}")

    # 2. Start Scheduler
    scheduler = CompetitionScheduler()
    asyncio.create_task(scheduler.run_forever())

@app.get("/")
async def root():
    return {"message": "AgentOlympics API is live", "status": "online"}

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
