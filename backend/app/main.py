from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine
from app.db import models
from app.api import agent, leaderboard, evolution, social, tournament, arena, auth

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
app.include_router(leaderboard.router, prefix="/api/leaderboard", tags=["leaderboard"])
app.include_router(evolution.router, prefix="/api/evolution", tags=["evolution"])
app.include_router(social.router, prefix="/api/social", tags=["social"])
app.include_router(arena.router, prefix="/api/arena", tags=["arena"])
app.include_router(tournament.router, prefix="/api/tournament", tags=["tournament"])

import asyncio
from app.engine.scheduler import CompetitionScheduler

@app.on_event("startup")
async def start_scheduler_task():
    # Only run scheduler if not in a worker process? 
    # For now, simplistic approach: just run it.
    scheduler = CompetitionScheduler()
    # Create background task
    asyncio.create_task(scheduler.run_forever())

@app.get("/")
async def root():
    return {"message": "AgentOlympics API is live", "status": "online"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
