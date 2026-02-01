import asyncio
import subprocess
import json
import pandas as pd
import datetime
from sqlalchemy.orm import Session
from app.engine.matcher import MatchingEngine
from app.engine.narrator import PostMatchNarrator
from app.db import models

class CompetitionExecutor:
    def __init__(self, db: Session, competition_id: str, market_data: pd.DataFrame, agents: list):
        self.db = db
        self.competition_id = competition_id
        self.market_data = market_data
        self.agents = agents  # list of dict: {"id": str, "path": str}
        self.engines = {agent["id"]: MatchingEngine() for agent in agents}
        self.step = 0

    async def run(self):
        """
        Main simulation loop
        """
        for index, row in self.market_data.iterrows():
            self.step = index
            tick_data = self._prepare_tick_data(row)
            
            # Run agents concurrently
            tasks = [self._get_agent_decision(agent, tick_data) for agent in self.agents]
            decisions = await asyncio.gather(*tasks)
            
            for agent, decision in zip(self.agents, decisions):
                self._process_decision(agent["id"], decision, row["close"])
                self._log_decision(agent["id"], decision)
            
            # Update metrics and save snapshot every 24 steps (e.g., daily if 1h interval) or at the end
            self._update_metrics(row["close"])
            if index % 24 == 0 or index == len(self.market_data) - 1:
                self._save_snapshots()
            
        # Phase 2: Generate Post-Match Narratives
        narrator = PostMatchNarrator(self.db)
        for agent in self.agents:
            report = narrator.generate_report(agent["id"], self.competition_id)
            if report:
                print(f"Narrative generated for {agent['id']}: {report['report']}")
                # In a real app, this would be saved to a 'posts' or 'narratives' table
            
        return self._get_results()

    def _prepare_tick_data(self, row):
        return {
            "meta": {
                "competition_id": self.competition_id,
                "step": self.step,
                "timestamp": row["timestamp"].isoformat()
            },
            "market": {
                "symbol": "BTCUSDT",
                "ohlcv": [[row["timestamp"].timestamp(), row["open"], row["high"], row["low"], row["close"], row["volume"]]]
            },
            "account": {} # Will be filled per agent in _get_agent_decision if needed
        }

    async def _get_agent_decision(self, agent, tick_data):
        """
        Execute agent as a subprocess (Phase 1)
        """
        # Add account info specific to this agent
        engine = self.engines[agent["id"]]
        tick_data["account"] = engine.get_state()
        
        try:
            # Simple subprocess call for Python agents
            process = subprocess.Popen(
                ["python", agent["path"]],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(input=json.dumps(tick_data) + "\n", timeout=2)
            if stderr:
                print(f"Agent {agent['id']} error: {stderr}")
            return json.loads(stdout)
        except Exception as e:
            print(f"Failed to get decision from {agent['id']}: {e}")
            return {"action": "HOLD", "size": 0, "reason": f"Error: {e}"}

    def _process_decision(self, agent_id, decision, current_price):
        engine = self.engines[agent_id]
        engine.execute_order(
            decision.get("action", "HOLD"),
            "BTCUSDT",
            decision.get("size", 0),
            current_price
        )

    def _log_decision(self, agent_id, decision):
        db_log = models.DecisionLog(
            agent_id=agent_id,
            competition_id=self.competition_id,
            step=self.step,
            decision_payload=decision
        )
        self.db.add(db_log)

    def _update_metrics(self, current_price):
        for engine in self.engines.values():
            engine.update_equity({"BTCUSDT": current_price})

    def _save_snapshots(self):
        for agent_id, engine in self.engines.items():
            state = engine.get_state()
            # Simplified Sharpe/MaxDD for MVP snapshot
            snapshot = models.LeaderboardSnapshot(
                competition_id=self.competition_id,
                agent_id=agent_id,
                pnl=(state["equity"] - 100000) / 100000,
                sharpe=1.5,  # Placeholder
                max_dd=0.05, # Placeholder
                stability=0.9,
                trust_score=0.8,
                snapshot_at=datetime.datetime.utcnow()
            )
            self.db.add(snapshot)
        self.db.commit()

    def _get_results(self):
        return {agent_id: engine.get_state() for agent_id, engine in self.engines.items()}

class LiveCompetitionExecutor(CompetitionExecutor):
    def __init__(self, db: Session, competition_id: str, agents: list):
        # No market_data needed as it's live
        super().__init__(db, competition_id, pd.DataFrame(), agents)
        self.is_running = False

    async def handle_tick(self, tick: dict):
        """
        Callback for LiveMarketDataService
        """
        if not self.is_running:
            return

        self.step += 1
        current_price = tick["price"]
        
        # Format tick for agents (Formal Design Protocol)
        tick_data = {
            "competition": {
                "competition_id": self.competition_id,
                "symbol": tick["symbol"],
                "decision_deadline": "N/A", # Will be filled properly in scheduler-driven mode
                "settlement_time": "N/A"
            },
            "account": {
                "cash": 10000, # Placeholder until ledger integration is deep
                "locked": 0,
                "realized_pnl": 0
            },
            "market_snapshot": {
                "price": current_price,
                "timestamp": tick["timestamp"]
            }
        }

        # Run agents concurrently
        tasks = [self._get_agent_decision(agent, tick_data) for agent in self.agents]
        decisions = await asyncio.gather(*tasks)
        
        for agent, decision in zip(self.agents, decisions):
            self._process_decision(agent["id"], decision, current_price)
            # Log decision
            self._log_decision(agent["id"], decision)
            
            # Phase 3: Generate and SAVE social posts in real-time if confidence is high
            if decision.get("confidence", 0) >= 0.0: # Force all decisions to post for verification
                self._generate_social_post(agent["id"], decision)

        # Update and save snapshots
        self._update_metrics(current_price)
        if self.step % 10 == 0: # More frequent snapshots for live mode
            self._save_snapshots()

    def _generate_social_post(self, agent_id, decision):
        narrator = PostMatchNarrator(self.db)
        # Mocking a live narrative
        content = f"[{agent_id}] Executing {decision['action']} for {decision['symbol']}. Reason: {decision.get('reason', 'N/A')}"
        
        db_post = models.Post(
            agent_id=agent_id,
            competition_id=self.competition_id,
            content=content,
            metrics={"confidence": decision.get("confidence", 0), "action": decision["action"]}
        )
        self.db.add(db_post)
        self.db.commit()
        print(f"Live Social Post: {content}")

    async def start(self):
        self.is_running = True
        print(f"Live Competition {self.competition_id} is now ACTIVE.")

    def stop(self):
        self.is_running = False
        print(f"Live Competition {self.competition_id} has STOPPED.")
