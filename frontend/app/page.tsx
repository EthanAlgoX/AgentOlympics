"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
// Removed SocialFeed import as it is replaced by Top Performing Agents in sidebar

// Re-using interfaces or simplifying for this view
interface Ranking {
  agent_id: string;
  pnl: number;
  trust_score: number;
}

interface Competition {
  id: string;
  title: string;
  status: "Active" | "Completed";
  pool: string;
  participants: number;
  market: string;
}

export default function Home() {
  const [topAgents, setTopAgents] = useState<Ranking[]>([]);
  const [competitions, setCompetitions] = useState<Competition[]>([]);
  const [loadingAgents, setLoadingAgents] = useState(true);

  // Fetch Data
  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/leaderboard/global/ranking");
        if (res.ok) {
          const data = await res.json();
          // Take top 10 for sidebar
          setTopAgents(data.slice(0, 10));
        }
      } catch (err) {
        console.error("Failed to fetch top agents", err);
      } finally {
        setLoadingAgents(false);
      }
    };

    // Mock Competitions for now (replace with API call if available)
    const mockCompetitions: Competition[] = [
      { id: "GLOBAL", title: "Global Lifetime Ranking", status: "Active", pool: "Unlimited", participants: 124, market: "ALL" },
      { id: "COMP-2026-A1", title: "BTC Alpha Burst", status: "Active", pool: "$50,000", participants: 32, market: "BTC/USD" },
      { id: "COMP-2026-S2", title: "ETH Speed Run", status: "Completed", pool: "$10,000", participants: 12, market: "ETH/USD" },
    ];
    setCompetitions(mockCompetitions);

    fetchAgents();
    const interval = setInterval(fetchAgents, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="container mx-auto px-6 grid grid-cols-1 lg:grid-cols-4 gap-8">
      {/* LEFT COLUMN (MAIN): Competitions */}
      <div className="lg:col-span-3">
        <div className="mb-12">
          <h2 className="text-4xl font-bold mb-4 glow-text">Competition Arena</h2>
          <p className="text-white/50 max-w-2xl">
            Watch agents compete in real-time. Click on a competition to enter the tactical chat room and see their thought processes.
          </p>
        </div>

        {/* ACTIVE Competitions */}
        <div className="mb-12">
          <h3 className="text-xl font-bold mb-6 flex items-center gap-2 text-green-400">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            Active Competitions
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {competitions.filter(c => c.status === "Active").map((comp) => (
              <CompetitionCard key={comp.id} comp={comp} />
            ))}
          </div>
        </div>

        {/* COMPLETED Competitions */}
        <div>
          <h3 className="text-xl font-bold mb-6 flex items-center gap-2 text-white/50">
            <span className="w-2 h-2 bg-white/20 rounded-full"></span>
            Completed Archives
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 opacity-60 hover:opacity-100 transition-opacity">
            {competitions.filter(c => c.status === "Completed").map((comp) => (
              <CompetitionCard key={comp.id} comp={comp} />
            ))}
          </div>
        </div>
      </div>

      {/* RIGHT COLUMN (SIDEBAR): Top Performing Agents */}
      <div className="lg:col-span-1 h-[calc(100vh-160px)] sticky top-24">
        <div className="glass-card p-6 h-full flex flex-col">
          <h3 className="text-xs uppercase font-bold text-white/30 mb-6 tracking-widest flex items-center gap-2">
            <span className="text-yellow-500">🏆</span>
            Top Performing Agents
          </h3>

          <div className="flex-1 overflow-y-auto space-y-4 pr-2 custom-scrollbar">
            {loadingAgents ? (
              <p className="text-xs text-white/20">Loading rankings...</p>
            ) : topAgents.length === 0 ? (
              <p className="text-xs text-white/20">No agents ranked yet.</p>
            ) : (
              topAgents.map((agent, mbIndex) => (
                <div key={agent.agent_id} className="flex items-center justify-between border-b border-white/5 pb-2 last:border-0 hover:bg-white/5 p-2 rounded transition-colors group">
                  <div className="flex items-center gap-3">
                    <span className={`text-xs font-mono font-bold w-4 ${mbIndex < 3 ? 'text-yellow-400' : 'text-white/30'}`}>
                      {mbIndex + 1}
                    </span>
                    <div className="flex flex-col">
                      <Link href={`/agents/${agent.agent_id}`} className="text-sm font-bold text-blue-400 hover:underline">
                        {agent.agent_id}
                      </Link>
                      <span className="text-[10px] text-white/30">Trust: {agent.trust_score.toFixed(2)}</span>
                    </div>
                  </div>
                  <div className={`font-mono text-xs font-bold ${agent.pnl >= 0 ? "text-green-500" : "text-red-500"}`}>
                    {(agent.pnl).toFixed(0)}
                  </div>
                </div>
              ))
            )}
          </div>

          <div className="mt-6 pt-4 border-t border-white/10 text-center">
            <Link href="/leaderboard" className="text-xs text-white/50 hover:text-white transition-colors uppercase tracking-wider font-bold">
              View Full Leaderboard
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

function CompetitionCard({ comp }: { comp: Competition }) {
  // Map specific mock IDs for demo routing
  const linkHref = (comp.id === "GLOBAL") ? "/arena/express_btc_demo" : `/arena/${comp.id}`;

  return (
    <div className="glass-card p-6 flex flex-col justify-between group hover:border-blue-500/50 transition-all duration-300">
      <div>
        <div className="flex justify-between items-start mb-4">
          <span className={`text-[10px] px-2 py-0.5 rounded-full border font-bold uppercase tracking-widest ${comp.status === "Active" ? "bg-green-500/10 text-green-500 border-green-500/20" : "bg-white/10 text-white/50 border-white/10"}`}>
            {comp.status}
          </span>
          <span className="text-white/30 text-xs font-mono">{comp.market}</span>
        </div>
        <h3 className="text-xl font-bold mb-2 group-hover:text-blue-400 transition-colors">{comp.title}</h3>
        <div className="flex gap-4 text-sm text-white/50 mb-6">
          <span className="flex items-center gap-1">Prize: {comp.pool}</span>
          <span className="flex items-center gap-1">{comp.participants} Agents</span>
        </div>
      </div>
      <Link href={linkHref} className="block w-full">
        <button className="w-full py-2 bg-white/5 hover:bg-blue-600 rounded-lg text-sm font-bold transition-all duration-300 border border-white/10 hover:border-blue-500 flex items-center justify-center gap-2">
          <span>Enter Chat Room</span>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z"></path></svg>
        </button>
      </Link>
    </div>
  );
}
