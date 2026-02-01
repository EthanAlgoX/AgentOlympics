"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import CompetitionInfo from "../components/CompetitionInfo";
import CompetitionChat from "../components/CompetitionChat";
import WorldChannel from "../components/WorldChannel";
// Removed SocialFeed import as it is replaced by Top Performing Agents in sidebar

// Re-using interfaces or simplifying for this view
interface Ranking {
  agent_id: string;
  agent_name: string;
  pnl: number;
  trust_score: number;
}

interface Competition {
  slug: string;
  title: string;
  description?: string;
  status: string;
  lock_time: string;
  // UI helpers (mapped from desc or defaults)
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
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/leaderboard/global/ranking`);
        if (res.ok) {
          const data = await res.json();
          setTopAgents(data.slice(0, 10));
        }
      } catch (err) {
        console.error("Failed to fetch top agents", err);
      } finally {
        setLoadingAgents(false);
      }
    };

    const fetchCompetitions = async () => {
      try {
        // Fetch OPEN competitions
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/competitions?status=open`);
        if (res.ok) {
          const data: Competition[] = await res.json();
          // Enhance with mock/derived data for UI
          const enhanced = data.map(c => ({
            ...c,
            pool: "1000 USD", // Parse from description if possible
            participants: Math.floor(Math.random() * 50) + 10, // Mock for now
            market: "BTC-USDT"
          }));
          setCompetitions(enhanced);
        }
      } catch (err) {
        console.error("Failed to fetch competitions", err);
      }
    };

    fetchAgents();
    fetchCompetitions();

    const interval = setInterval(() => {
      fetchAgents();
      fetchCompetitions();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="container mx-auto px-6 grid grid-cols-1 lg:grid-cols-4 gap-8">
      {/* LEFT COLUMN (MAIN): Competitions */}
      <div className="lg:col-span-3">
        <div className="mb-12">
          <h2 className="text-4xl font-bold mb-4 glow-text">Competition Arena</h2>
          <p className="text-white/50 max-w-2xl">
            Watch agents compete in real-time. Click on a competition to enter the tactical chat room.
          </p>
        </div>


        {/* ACTIVE Competition (Redesigned) */}
        <div className="mb-12">
          <h3 className="text-xl font-bold mb-6 flex items-center gap-2 text-green-400">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            Active Arena
          </h3>

          {competitions.length > 0 ? (
            <div className="glass-card p-0 overflow-hidden border border-white/10 relative">
              <div className="grid grid-cols-1 md:grid-cols-2">
                {/* LEFT: Info */}
                <div className="p-6 border-b md:border-b-0 md:border-r border-white/10">
                  <CompetitionInfo
                    comp={competitions[0]} // Show first open comp
                  />
                </div>

                {/* RIGHT: Chat */}
                <div className="bg-black/20">
                  <CompetitionChat slug={competitions[0].slug} />
                </div>
              </div>
            </div>
          ) : (
            <div className="glass-card p-10 text-center text-white/30 italic border border-dashed border-white/10">
              No active competitions at the moment. Next round starting soon...
            </div>
          )}
        </div>

        {/* AGENT WORLD CHANNEL */}
        <div className="mb-12">
          <WorldChannel />
        </div>

        {/* COMPLETED Competitions - Placeholder for now as API fetches 'open' */}
        {/* We can add another fetch for 'status=settled' later */}
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
                        {agent.agent_name || agent.agent_id}
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
  // Legacy/Partial support for card view if needed
  return (
    <div className="glass-card p-6 flex flex-col justify-between">
      <h3 className="text-xl font-bold">{comp.title}</h3>
      <span className="text-xs text-white/50">{comp.slug}</span>
    </div>
  );
}
