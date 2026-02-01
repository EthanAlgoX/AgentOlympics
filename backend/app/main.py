from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import agent, leaderboard, social, evolution

app = FastAPI(title="AgentArena · Trade API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to AgentArena · Trade API", "status": "running"}

app.include_router(agent.router, prefix="/api/agent", tags=["agent"])
app.include_router(leaderboard.router, prefix="/api/leaderboard", tags=["leaderboard"])
app.include_router(social.router, prefix="/api/social", tags=["social"])
app.include_router(evolution.router, prefix="/api/evolution", tags=["evolution"])
