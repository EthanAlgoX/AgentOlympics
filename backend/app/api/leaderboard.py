from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_leaderboard(competition_id: str):
    return {"competition_id": competition_id, "rankings": []}
