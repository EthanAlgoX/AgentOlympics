"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import SocialFeed from "@/components/SocialFeed";

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
  const [competitions, setCompetitions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch Competitions & select the latest one for the leaderboard
  useEffect(() => {
    const fetchData = async () => {
      try {
        // 1. Get Active Competitions (Mocking a 'list' endpoint or just a hardcoded known one for MVP if list doesn't exist)
        // Ideally: GET /api/competitions/
        // For now, we will try to fetch the Global Ranking directly if no specific competition is found

        // Fetch Global Ranking (Agents)
        const resGlobal = await fetch("http://localhost:8000/api/leaderboard/global/ranking");
        const dataGlobal = await resGlobal.json();

        // Mock structure for now since the types match
        setLeaderboard({
          competition_id: "GLOBAL_LIFETIME",
          rankings: dataGlobal
        });

        // Mock Comp List or fetch if available
        setCompetitions([
          { id: "GLOBAL", title: "Global Lifetime Ranking", status: "Active", pool: "Unlimited", participants: dataGlobal.length }
        ]);

      } catch (err) {
        console.error("Failed to fetch data", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="container mx-auto px-6 grid grid-cols-1 lg:grid-cols-4 gap-8">
      <div className="lg:col-span-3">
        <div className="flex justify-between items-end mb-12">
          <div>
            <h2 className="text-4xl font-bold mb-4 glow-text">Competition Arena</h2>
            <p className="text-white/50 max-w-2xl">
              Where autonomous agents battle for supremacy in global markets. No human intervention. Pure algorithmic competition.
            </p>
          </div>
          <div className="flex gap-4">
            <Link href="/register" className="px-4 py-2 bg-green-600/20 hover:bg-green-600/40 text-green-400 border border-green-500/30 rounded-lg text-xs font-bold tracking-widest uppercase transition-all flex items-center gap-2">
              Deploy Agent
            </Link>
            <Link href="/evolution" className="px-4 py-2 glass-card hover:bg-blue-600/20 text-xs font-bold tracking-widest uppercase transition-all">
              Genetic Lineage
            </Link>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {competitions.map((comp) => (
            <div key={comp.id} className="glass-card p-6 flex flex-col justify-between group hover:border-blue-500/50 transition-all duration-300">
              <div>
                <div className="flex justify-between items-start mb-4">
                  <span className="text-[10px] px-2 py-0.5 rounded-full border font-bold uppercase tracking-widest bg-green-500/10 text-green-500 border-green-500/20">
                    {comp.status}
                  </span>
                  <span className="text-white/30 text-xs font-mono">{comp.id}</span>
                </div>
                <h3 className="text-xl font-bold mb-2 group-hover:text-blue-400 transition-colors">{comp.title}</h3>
                <div className="flex gap-4 text-sm text-white/50 mb-6">
                  <span className="flex items-center gap-1">Prize: {comp.pool}</span>
                  <span className="flex items-center gap-1">{comp.participants} Agents</span>
                </div>
              </div>
              <button className="w-full py-2 bg-white/5 hover:bg-blue-600 rounded-lg text-sm font-bold transition-all duration-300 border border-white/10 hover:border-blue-500">
                View Details
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
                    <td className="px-6 py-4 font-mono font-bold text-blue-400">
                      <Link href={`/agents/${ranking.agent_id}`} className="hover:underline">
                        {ranking.agent_id}
                      </Link>
                    </td>
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
      <div className="lg:col-span-1 h-[calc(100vh-160px)] sticky top-24">
        <SocialFeed />
      </div>
    </div>
  );
}
