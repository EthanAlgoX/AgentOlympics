from pydantic import BaseModel, Field
from typing import List, Optional

class AgentCapabilities(BaseModel):
    market_data: List[str] = Field(default=["OHLCV"])
    actions: List[str] = Field(default=["buy", "sell", "hold"])
    risk_limits: bool = True

class AgentManifest(BaseModel):
    agent_name: str
    author: str
    version: str = "0.1.0"
    description: str
    languages: List[str] = ["python"]
    entrypoint: str = "strategy.py"
    capabilities: Optional[AgentCapabilities] = None

def validate_manifest(data: dict):
    try:
        manifest = AgentManifest(**data)
        return True, manifest
    except Exception as e:
        return False, str(e)
