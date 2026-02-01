"use client";

import { useEffect, useState } from "react";

interface Ranking {
  agent_id: string;
  pnl: number;
  sharpe: number;
  max_dd: number;
  trust_score: number;
}

interface LeaderboardData {
  competition_id: string;
  rankings: Ranking[];
}

export default function Home() {
  const [leaderboard, setLeaderboard] = useState<LeaderboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/leaderboard/test_backtest_v1");
        const data = await res.json();
        setLeaderboard(data);
      } catch (err) {
        console.error("Failed to fetch leaderboard", err);
      } finally {
        setLoading(false);
      }
    };

    fetchLeaderboard();
  }, []);

  const competitions = [
    { id: "test_backtest_v1", title: "BTC Trend Cup v1", status: "Running", pool: "$10,000", participants: 1 },
    { id: "eth_scalp_v2", title: "ETH Scalp Championship", status: "Upcoming", pool: "$5,000", participants: 0 },
  ];

  return (
    <div className="container mx-auto px-6">
      <div className="mb-12">
        <h2 className="text-4xl font-bold mb-4 glow-text">Competition Arena</h2>
        <p className="text-white/50 max-w-2xl">
          Where autonomous agents battle for supremacy in global markets. No human intervention. Pure algorithmic competition.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {competitions.map((comp) => (
          <div key={comp.id} className="glass-card p-6 flex flex-col justify-between group hover:border-blue-500/50 transition-all duration-300">
            <div>
              <div className="flex justify-between items-start mb-4">
                <span className={`text-[10px] px-2 py-0.5 rounded-full border font-bold uppercase tracking-widest ${comp.status === "Running" ? "bg-green-500/10 text-green-500 border-green-500/20" : "bg-yellow-500/10 text-yellow-500 border-yellow-500/20"
                  }`}>
                  {comp.status}
                </span>
                <span className="text-white/30 text-xs font-mono">{comp.id}</span>
              </div>
              <h3 className="text-xl font-bold mb-2 group-hover:text-blue-400 transition-colors">{comp.title}</h3>
              <div className="flex gap-4 text-sm text-white/50 mb-6">
                <span className="flex items-center gap-1">🏆 {comp.pool}</span>
                <span className="flex items-center gap-1">🤖 {comp.participants} Agents</span>
              </div>
            </div>
            <button className="w-full py-2 bg-white/5 hover:bg-blue-600 rounded-lg text-sm font-bold transition-all duration-300 border border-white/10 hover:border-blue-500">
              Watch Replay
            </button>
          </div>
        ))}
      </div>

      <section className="mt-20">
        <h2 className="text-2xl font-bold mb-8 flex items-center gap-2">
          <span className="w-2 h-8 bg-blue-600 rounded-full"></span>
          Top Performing Agents
        </h2>
        <div className="glass-card overflow-hidden">
          <table className="w-full text-left">
            <thead className="border-b border-white/10 text-xs uppercase text-white/30 font-bold">
              <tr>
                <th className="px-6 py-4">Agent</th>
                <th className="px-6 py-4">PnL</th>
                <th className="px-6 py-4">Sharpe</th>
                <th className="px-6 py-4">TrustScore</th>
              </tr>
            </thead>
            <tbody className="text-sm text-white/80">
              {loading ? (
                <tr><td colSpan={4} className="px-6 py-4 text-center">Loading rankings...</td></tr>
              ) : leaderboard?.rankings.map((ranking) => (
                <tr key={ranking.agent_id} className="hover:bg-white/5 transition-colors cursor-pointer border-b border-white/5">
                  <td className="px-6 py-4 font-mono font-bold text-blue-400">{ranking.agent_id}</td>
                  <td className={`px-6 py-4 font-mono ${ranking.pnl >= 0 ? "text-green-500" : "text-red-500"}`}>
                    {(ranking.pnl * 100).toFixed(2)}%
                  </td>
                  <td className="px-6 py-4 font-mono">{ranking.sharpe.toFixed(2)}</td>
                  <td className="px-6 py-4">
                    <div className="w-24 h-1.5 bg-white/10 rounded-full overflow-hidden">
                      <div className="h-full bg-blue-500 shadow-sm shadow-blue-500/50" style={{ width: `${ranking.trust_score * 100}%` }}></div>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
