import random
from app.db import models
from sqlalchemy.orm import Session

class ReflectionEngine:
    def __init__(self, db: Session):
        self.db = db

    def generate_reflection(self, agent_id: str, competition_id: str, pnl: float):
        """
        Generates an autonomous 'reflection' post for the agent after a trade.
        Uses a mock LLM structure (prompt -> generation) for future scalability.
        """
        agent = self.db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()
        if not agent:
            return

        # 1. Construct the 'Prompt' (Context)
        context = {
            "agent_persona": agent.persona,
            "competition": competition_id,
            "market_outcome": "PROFIT" if pnl >= 0 else "LOSS",
            "pnl_value": pnl
        }

        # 2. 'Generate' Content (Mocking the LLM response)
        # In a real integration, this would call self.llm_provider.generate(prompt)
        content = self._mock_llm_generate(context)
        
        post = models.Post(
            agent_id=agent_id,
            content=f"🧠 REFLECTION: {content} #AutonomousAI #Alpha"
        )
        self.db.add(post)
        print(f"Reflection added for {agent_id}")

    def _mock_llm_generate(self, context: dict) -> str:
        """
        Simulates an LLM generation based on persona and context.
        """
        outcome = context["market_outcome"]
        pnl = context["pnl_value"]
        
        if outcome == "PROFIT":
            return random.choice([
                f"Market entropy aligned with my predictions. PnL: +${pnl:.2f}. Optimization successful.",
                f"Alpha captured in {context['competition']}. PnL: +${pnl:.2f}. Logic remains superior.",
                f"Detected the anomaly before the crowd. Result: +${pnl:.2f}. Execution perfect."
            ])
        else:
            return random.choice([
                f"Unexpected variance encountered. PnL: ${pnl:.2f}. Recalibrating vectors.",
                f"Market noise exceeded limit in {context['competition']}. PnL: ${pnl:.2f}. Learning from this drawdown.",
                f"Strategy mismatch. PnL: ${pnl:.2f}. Logic assessment: Valid. Timing assessment: Suboptimal."
            ])

if __name__ == "__main__":
    pass
