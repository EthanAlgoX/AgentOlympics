from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from pydantic import BaseModel
import uuid
import datetime
from typing import List, Optional

router = APIRouter()

class AgentPublic(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    created_at: datetime.datetime
    is_active: bool

    class Config:
        from_attributes = True

@router.get("/list", response_model=List[AgentPublic])
async def list_agents(db: Session = Depends(get_db)):
    return db.query(models.Agent).all()
