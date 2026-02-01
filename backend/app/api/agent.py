from fastapi import APIRouter

router = APIRouter()

@router.post("/register")
async def register_agent():
    return {"message": "Agent registration endpoint"}

@router.post("/decision")
async def submit_decision():
    return {"message": "Decision submission endpoint"}

@router.post("/heartbeat")
async def agent_heartbeat():
    return {"message": "Agent heartbeat endpoint"}
