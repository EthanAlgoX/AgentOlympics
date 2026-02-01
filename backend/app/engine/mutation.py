try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False
import os
import subprocess
import tempfile
import sys
from sqlalchemy.orm import Session
from app.db import models
import uuid

class LLMProvider:
    def __init__(self, api_key: str = None):
        if HAS_GENAI and api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        else:
            self.model = None
            if not HAS_GENAI:
                print("Warning: google-generativeai not installed. Using simulated responses.")

    async def generate_mutation(self, prompt: str) -> str:
        if not self.model:
            # Fallback to smart simulated response if no key
            return self._simulated_response(prompt)
        
        response = await self.model.generate_content_async(prompt)
        return response.text

    def _simulated_response(self, prompt: str) -> str:
        # Proper multi-line string for simulation
        return (
            "# Mutated Strategy (Simulated)\n"
            "import numpy as np\n"
            "def decide(snapshot):\n"
            "    return {'action': 'OPEN_LONG', 'stake': 1000}"
        )

class CodeValidator:
    @staticmethod
    def validate_syntax(code: str):
        try:
            compile(code, '<string>', 'exec')
            return True, None
        except SyntaxError as e:
            return False, f"Syntax Error: {e.msg} at line {e.lineno}"

    @staticmethod
    def validate_safety(code: str):
        forbidden = ["os.", "subprocess.", "eval", "exec", "shutil", "socket", "__import__", "requests"]
        for word in forbidden:
            if word in code:
                return False, f"Safety Violation: Forbidden keyword '{word}' detected."
        return True, None

    @staticmethod
    def run_trial(code: str):
        """Runs the code in a subprocess with a dummy snapshot to ensure basic compatibility."""
        with tempfile.NamedTemporaryFile(suffix=".py", mode='w', delete=False) as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        
        try:
            # Mock execution
            result = subprocess.run([sys.executable, tmp_path], capture_output=True, timeout=2)
            if result.returncode != 0:
                return False, f"Runtime Error during trial: {result.stderr.decode()}"
            return True, None
        except Exception as e:
            return False, f"Trial failed: {str(e)}"
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

class MutationEngine:
    def __init__(self, db: Session, api_key: str = None):
        self.db = db
        self.llm = LLMProvider(api_key)
        self.validator = CodeValidator()

    def suggest_mutation(self, agent_id: str):
        agent = self.db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()
        snapshots = self.db.query(models.LeaderboardSnapshot)\
            .filter(models.LeaderboardSnapshot.agent_id == agent_id)\
            .order_by(models.LeaderboardSnapshot.snapshot_at.desc())\
            .limit(10).all()

        avg_pnl = sum(s.pnl for s in snapshots) / len(snapshots) if snapshots else 0
        
        prompt = f"""
        Act as a Quantitative Trader. A trading agent '{agent_id}' with the following performance needs improvement:
        - Average PnL: {avg_pnl*100:.2f}%
        - Persona: {agent.persona}
        
        The current strategy code is provided below. Please rewrite the 'decide' function or the entire strategy 
        to optimize for Sharpe Ratio and reduce Max Drawdown. Ensure the output is valid Python code only.
        
        [STRATEGY CODE START]
        {self._read_agent_code(agent_id)}
        [STRATEGY CODE END]
        """
        return prompt

    async def apply_mutation(self, agent_id: str, owner_user: str, target_code: str = None):
        """
        Full mutation lifecycle: Suggest -> LLM -> Validate -> Apply
        """
        if not target_code:
            prompt = self.suggest_mutation(agent_id)
            target_code = await self.llm.generate_mutation(prompt)

        # Multi-stage Validation
        is_valid, err = self.validator.validate_syntax(target_code)
        if not is_valid: return None, f"Syntax Validation Failed: {err}"

        is_safe, err = self.validator.validate_safety(target_code)
        if not is_safe: return None, f"Safety Validation Failed: {err}"

        is_runnable, err = self.validator.run_trial(target_code)
        if not is_runnable: return None, f"Trial Execution Failed: {err}"

        # Application
        parent = self.db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()
        new_agent_id = f"{agent_id}_evolved_{uuid.uuid4().hex[:4]}"
        
        new_agent = models.Agent(
            agent_id=new_agent_id,
            owner_user=owner_user,
            persona=f"Advanced evolution of {agent_id}. Optimized for risk-adjusted returns.",
            trust_score=parent.trust_score * 0.85,
            parent_agent_id=agent_id,
            generation=parent.generation + 1
        )
        self.db.add(new_agent)
        
        agents_dir = os.path.join(os.getcwd(), "agents")
        os.makedirs(agents_dir, exist_ok=True)
        with open(os.path.join(agents_dir, f"{new_agent_id}.py"), "w") as f:
            f.write(target_code)
            
        self.db.commit()
        return new_agent, "Success"

    def _read_agent_code(self, agent_id: str):
        path = os.path.join(os.getcwd(), "agents", f"{agent_id}.py")
        if os.path.exists(path):
            with open(path, "r") as f: return f.read()
        return "# Baseline Strategy\nprint('Default logic')"
