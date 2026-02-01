import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.db.session import SessionLocal
from app.db import models

def list_agents():
    db = SessionLocal()
    agents = db.query(models.Agent).all()
    print(f"Found {len(agents)} agents:")
    for a in agents:
        print(f"- {a.agent_id} ({a.persona}) [Claimed: {a.is_claimed}]")

if __name__ == "__main__":
    list_agents()
