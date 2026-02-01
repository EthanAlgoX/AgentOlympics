"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

export default function AgentProfile() {
    const { id } = useParams();
    const [stats, setStats] = useState<any>(null);

    useEffect(() => {
        fetch(`http://localhost:8000/api/leaderboard/agents/${id}`)
            .then(res => res.json())
            .then(data => setStats(data));
    }, [id]);

    if (!stats) return <div className="p-20 text-center">Loading Profile...</div>;

    return (
        <div className="container mx-auto px-6">
            <div className="glass-card p-12 mb-12 relative overflow-hidden">
                <div className="absolute top-0 right-0 p-8 opacity-10 text-8xl font-bold font-mono">AGENT</div>
                <h2 className="text-4xl font-bold text-blue-400 mb-2 font-mono">{stats.agent.agent_id}</h2>
                <p className="text-white/50 mb-8 max-w-xl">{stats.agent.persona}</p>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                    <div>
                        <div className="text-xs text-white/30 uppercase font-bold mb-1">Trust Score</div>
                        <div className="text-2xl font-bold">{(stats.agent.trust_score * 100).toFixed(0)}</div>
                    </div>
                    <div>
                        <div className="text-xs text-white/30 uppercase font-bold mb-1">Competitions</div>
                        <div className="text-2xl font-bold">{stats.ongoing_competitions}</div>
                    </div>
                    <div>
                        <div className="text-xs text-white/30 uppercase font-bold mb-1">Created</div>
                        <div className="text-2xl font-bold">{new Date(stats.agent.created_at).toLocaleDateString()}</div>
                    </div>
                    <div>
                        <div className="text-xs text-white/30 uppercase font-bold mb-1">Status</div>
                        <div className="text-xs px-2 py-1 rounded bg-green-500/10 text-green-500 border border-green-500/20 inline-block">ACTIVE</div>
                    </div>
                </div>
            </div>

            <h3 className="text-xl font-bold mb-6">Recent Decision History</h3>
            <div className="glass-card p-6 opacity-50 italic text-center text-sm">
                Decision logs for this agent are being processed.
            </div>
        </div>
    );
}
