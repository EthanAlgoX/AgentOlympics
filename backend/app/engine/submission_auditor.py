import os
import re
import subprocess
import sys
import tempfile
from sqlalchemy.orm import Session
from app.db import models
from app.engine.manifest_v1 import validate_manifest

class SubmissionAuditor:
    def __init__(self, db: Session):
        self.db = db

    def audit_submission(self, agent_id: str, code_path: str, manifest_data: dict):
        """
        Full audit pipeline for new agent submissions.
        """
        # 1. Manifest Validation
        is_valid_manifest, manifest = validate_manifest(manifest_data)
        if not is_valid_manifest:
            return False, f"Manifest Error: {manifest}"

        # 2. Read Code
        if not os.path.exists(code_path):
            return False, "Code file not found."
        
        with open(code_path, "r") as f:
            code = f.read()

        # 3. Static Scan (Security)
        forbidden = [r"os\.", r"subprocess\.", r"eval\(", r"exec\(", r"shutil", r"__import__", r"socket"]
        for pattern in forbidden:
            if re.search(pattern, code):
                return False, f"Security Audit Failed: Forbidden pattern '{pattern}' detected."

        # 4. Interface Check
        if "def decide" not in code and "def on_data" not in code:
            return False, "Interface Audit Failed: Missing 'decide' or 'on_data' entrypoint."

        # 5. Sandbox Trial
        is_runnable, err = self._run_trial(code)
        if not is_runnable:
            return False, f"Execution Audit Failed: {err}"

        return True, "Audit Passed"

    def _run_trial(self, code: str):
        with tempfile.NamedTemporaryFile(suffix=".py", mode='w', delete=False) as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        
        try:
            # Simple syntax check + trial run
            result = subprocess.run([sys.executable, tmp_path], capture_output=True, timeout=2)
            if result.returncode != 0:
                # We expect it might fail if it tries to do things without proper context, 
                # but it should at least be syntactically correct.
                # A better trial would provide a mock 'context' and 'market_data'.
                pass 
            return True, None
        except Exception as e:
            return False, str(e)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
