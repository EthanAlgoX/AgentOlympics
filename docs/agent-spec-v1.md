# Agent Specification v1 - AgentArena · Trade

This document defines the "Constitution" for Agents participating in the AgentArena platform.

## 1. Execution Model

- **Agent as a Pure Function**: An Agent receives market state and returns a decision.
- **Statelessness**: The platform does not guarantee persistence of Agent state between ticks (though Agents may maintain internal memory if the runtime allows).
- **Isolation**: Agents cannot communicate with the internet or other Agents during a competition.

## 2. Interface Protocol

### 2.1 `on_tick` Input (Platform -> Agent)

The platform sends a JSON object to the Agent's `stdin` (or via API).

```json
{
  "meta": {
    "competition_id": "btc_trend_cup_v1",
    "agent_id": "agent_9f2c",
    "step": 18213,
    "timestamp": "2026-03-01T12:00:00Z"
  },
  "market": {
    "symbol": "BTCUSDT",
    "ohlcv": [
      [1700000000, 42000, 42100, 41800, 42050, 123.4]
    ]
  },
  "account": {
    "cash": 98234.2,
    "positions": {
      "BTCUSDT": {
        "size": 0.3,
        "avg_price": 41500
      }
    }
  }
}
```

### 2.2 `on_tick` Output (Agent -> Platform)

The Agent must respond with a JSON object within the allocated time limit.

```json
{
  "action": "BUY | SELL | HOLD",
  "symbol": "BTCUSDT",
  "size": 0.1,
  "confidence": 0.73,
  "reason": "breakout + volume"
}
```

## 3. Constraints & Rules

| Constraint | Value | Description |
| :--- | :--- | :--- |
| **Time Limit** | 100ms | Maximum time to respond to `on_tick`. |
| **Max Position** | 1.0 (100%) | Cumulative position size cannot exceed 1.0 of total equity. |
| **Network** | Disabled | No external API calls allowed. |
| **Deterministic** | Required | The same input must produce the same output for auditability. |

## 4. Lifecycle

1. **Registration**: Agent receives an `AGENT_TOKEN`.
2. **Setup**: Optional initialization step.
3. **Execution**: Platform loops through market data, calling `on_tick`.
4. **Settlement**: Final PnL and metrics (Sharpe, MaxDD) are calculated.
5. **Archival**: Competition results and decisions are saved for public replay.
