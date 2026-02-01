from fastapi import FastAPI
from app.api import agent, leaderboard

app = FastAPI(title="AgentArena · Trade API")

@app.get("/")
async def root():
    return {"message": "Welcome to AgentArena · Trade API", "status": "running"}

app.include_router(agent.router, prefix="/api/agent", tags=["agent"])
app.include_router(leaderboard.router, prefix="/api/leaderboard", tags=["leaderboard"])
