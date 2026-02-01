import os
import json
from sqlalchemy.orm import Session
from app.db import models
from app.engine.narrator import PostMatchNarrator
import uuid

class MutationEngine:
    def __init__(self, db: Session):
        self.db = db

    def suggest_mutation(self, agent_id: str):
        """
        Uses historical performance to suggest code improvements.
        In Phase 4 MVP, this provides a structured instruction for the LLM.
        """
        agent = self.db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()
        snapshots = self.db.query(models.LeaderboardSnapshot)\
            .filter(models.LeaderboardSnapshot.agent_id == agent_id)\
            .order_by(models.LeaderboardSnapshot.snapshot_at.desc())\
            .limit(10).all()

        if not snapshots:
            return "No performance data available for mutation."

        avg_pnl = sum(s.pnl for s in snapshots) / len(snapshots)
        
        # Construct mutation prompt
        perf_summary = f"Agent {agent_id} has average PnL of {avg_pnl*100:.2f}% over last {len(snapshots)} snapshots."
        
        mutation_instruction = {
            "performance_summary": perf_summary,
            "target_agent": agent_id,
            "goals": [
                "Increase Sharpe ratio",
                "Reduce max drawdown" if any(s.max_dd > 0.1 for s in snapshots) else "Optimize entry/exit timing",
                "Refine risk parameters"
            ],
            "action": "MUTATE_CODE"
        }
        
        return mutation_instruction

    def apply_mutation(self, agent_id: str, owner_user: str, mutated_code: str):
        """
        Saves the mutated code as a new 'child' agent and creates a new file.
        """
        parent = self.db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()
        if not parent:
            return None

        # 1. Create a new agent record marked as mutated child
        new_agent_id = f"{agent_id}_mutated_{uuid.uuid4().hex[:4]}"
        new_agent = models.Agent(
            agent_id=new_agent_id,
            owner_user=owner_user,
            persona=f"Mutated from {agent_id}. Targeted performance optimization.",
            trust_score=parent.trust_score * 0.8, # Initial trust drop
            parent_agent_id=agent_id,
            generation=parent.generation + 1
        )
        self.db.add(new_agent)
        
        # 2. Save the code to a new file in 'agents' directory
        # In this implementation, we assume files are relative to project root
        curr_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        agents_dir = os.path.join(curr_dir, "agents")
        os.makedirs(agents_dir, exist_ok=True)
        
        new_file_name = f"{new_agent_id}.py"
        new_file_path = os.path.join(agents_dir, new_file_name)
        
        with open(new_file_path, "w") as f:
            f.write(mutated_code)
            
        self.db.commit()
        print(f"Agent mutated: {new_agent_id} saved to {new_file_path}")
        
        return new_agent
