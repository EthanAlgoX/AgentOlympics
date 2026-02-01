# AgentArena Base Image v1
FROM python:3.10-slim

WORKDIR /app

# Install standard trading and math libraries
RUN pip install --no-cache-dir \
    pandas \
    numpy \
    scipy \
    scikit-learn \
    requests

# Standardize the execution entrypoint
# The agent script should be named 'agent_main.py' and reside in /app
# Decisions are communicated via stdout
CMD ["python", "agent_main.py"]
