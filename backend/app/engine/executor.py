import asyncio
import pandas as pd
from app.engine.matcher import MatchingEngine

class CompetitionExecutor:
    def __init__(self, competition_id: str, market_data: pd.DataFrame, agents: list):
        self.competition_id = competition_id
        self.market_data = market_data
        self.agents = agents
        self.engines = {agent["id"]: MatchingEngine() for agent in agents}
        self.step = 0

    async def run(self):
        """
        Main simulation loop
        """
        for index, row in self.market_data.iterrows():
            self.step = index
            tick_data = self._prepare_tick_data(row)
            
            # In a real scenario, this would call Agent APIs concurrently
            for agent in self.agents:
                decision = await self._get_agent_decision(agent, tick_data)
                self._process_decision(agent["id"], decision, row["close"])
            
            # Update metrics
            self._update_metrics(row["close"])
            
        return self._get_results()

    def _prepare_tick_data(self, row):
        return {
            "symbol": "BTCUSDT",
            "ohlcv": [[row["timestamp"], row["open"], row["high"], row["low"], row["close"], row["volume"]]]
        }

    async def _get_agent_decision(self, agent, tick_data):
        # Mocking agent decision for now
        # In Phase 1, this will call the subprocess/API
        return {"action": "HOLD", "size": 0}

    def _process_decision(self, agent_id, decision, current_price):
        engine = self.engines[agent_id]
        engine.execute_order(
            decision.get("action", "HOLD"),
            "BTCUSDT",
            decision.get("size", 0),
            current_price
        )

    def _update_metrics(self, current_price):
        for engine in self.engines.values():
            engine.update_equity({"BTCUSDT": current_price})

    def _get_results(self):
        return {agent_id: engine.get_state() for agent_id, engine in self.engines.items()}
