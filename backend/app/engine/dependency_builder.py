import os
import subprocess
import sys

class DependencyBuilder:
    def __init__(self, agents_root: str):
        self.agents_root = agents_root

    def setup_agent_env(self, agent_id: str, requirements: list = None):
        """
        Creates a virtual environment and installs dependencies for a specific agent.
        """
        agent_dir = os.path.join(self.agents_root, agent_id)
        os.makedirs(agent_dir, exist_ok=True)
        
        venv_path = os.path.join(agent_dir, "venv")
        if not os.path.exists(venv_path):
            print(f"Creating venv for {agent_id}...")
            subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)

        if requirements:
            req_file = os.path.join(agent_dir, "requirements.txt")
            with open(req_file, "w") as f:
                f.write("\n".join(requirements))
            
            pip_path = os.path.join(venv_path, "bin", "pip")
            print(f"Installing requirements for {agent_id}...")
            subprocess.run([pip_path, "install", "-r", req_file], check=True)
        
        return venv_path

    def get_agent_python(self, agent_id: str):
        return os.path.join(self.agents_root, agent_id, "venv", "bin", "python")
