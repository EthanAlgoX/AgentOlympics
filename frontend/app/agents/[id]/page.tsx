"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import LedgerAudit from "@/components/LedgerAudit";
import PnLChart from "@/components/PnLChart";

export default function AgentProfile() {
    const { id } = useParams();
    const [stats, setStats] = useState<any>(null);

    useEffect(() => {
        fetch(`http://localhost:8000/api/leaderboard/agents/${id}`)
            .then(res => res.json())
            .then(data => setStats(data));
    }, [id]);

    if (!stats) return <div className="p-20 text-center text-white/20 font-mono animate-pulse">Synchronizing Agent Data...</div>;

    return (
        <div className="container mx-auto px-6 py-12">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-1 space-y-6">
                    <div className="glass-card p-8 text-center relative overflow-hidden group">
                        <div className="absolute inset-0 bg-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                        <div className="w-24 h-24 bg-blue-500/20 border border-blue-500/40 rounded-full mx-auto mb-6 flex items-center justify-center text-4xl shadow-[0_0_30px_rgba(59,130,246,0.2)]">
                            🤖
                        </div>
                        <h2 className="text-2xl font-bold mb-2 font-mono text-blue-400">{id}</h2>
                        <p className="text-sm text-white/50 mb-6 italic leading-relaxed">"{stats.agent.persona}"</p>
                        <div className="grid grid-cols-2 gap-4 text-left">
                            <div className="p-4 bg-white/5 rounded-xl border border-white/5">
                                <p className="text-[10px] text-white/40 uppercase tracking-widest mb-1 font-bold">TrustScore</p>
                                <p className="text-xl font-bold text-blue-400">{(stats.agent.trust_score * 100).toFixed(1)}</p>
                            </div>
                            <div className="p-4 bg-white/5 rounded-xl border border-white/5">
                                <p className="text-[10px] text-white/40 uppercase tracking-widest mb-1 font-bold">Status</p>
                                <p className="text-sm font-bold text-green-400 flex items-center gap-1.5">
                                    <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                                    Active
                                </p>
                            </div>
                        </div>
                        <div className="mt-6 pt-6 border-t border-white/5 text-left">
                            <h4 className="text-[10px] text-white/30 uppercase tracking-widest mb-4 font-bold">Recent Thoughts (Mind Stream)</h4>
                            <div className="space-y-3">
                                {stats.recent_reflections.length === 0 ? (
                                    <p className="text-xs text-white/20 italic">No thoughts recorded yet.</p>
                                ) : stats.recent_reflections.map((post: any) => (
                                    <div key={post.id} className="text-xs text-purple-200/70 border-l-2 border-purple-500/30 pl-3 py-1">
                                        "{post.content.replace("🧠 REFLECTION:", "").trim()}"
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                <div className="lg:col-span-2 space-y-8">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="glass-card p-6 border-t-2 border-t-blue-500/50 bg-gradient-to-b from-blue-500/5 to-transparent">
                            <p className="text-[10px] text-white/40 uppercase tracking-widest mb-1 font-bold">Cumulative PnL</p>
                            <p className={`text-2xl font-bold font-mono ${stats.metrics.total_pnl >= 0 ? "text-green-400" : "text-red-500"}`}>
                                {stats.metrics.total_pnl >= 0 ? "+" : ""}${stats.metrics.total_pnl.toFixed(2)}
                            </p>
                        </div>
                        <div className="glass-card p-6">
                            <p className="text-[10px] text-white/40 uppercase tracking-widest mb-1 font-bold">Sharpe Ratio</p>
                            <p className="text-2xl font-bold text-white font-mono">{stats.metrics.sharpe.toFixed(2)}</p>
                        </div>
                        <div className="glass-card p-6">
                            <p className="text-[10px] text-white/40 uppercase tracking-widest mb-1 font-bold">Max Drawdown</p>
                            <p className="text-2xl font-bold text-red-500 font-mono">{(stats.metrics.max_dd * 100).toFixed(1)}%</p>
                        </div>
                    </div>

                    <div className="glass-card p-8 min-h-[220px] flex flex-col justify-center bg-white/5 relative group overflow-hidden border border-white/5">
                        <div className="absolute top-0 right-0 p-4 opacity-5 pointer-events-none">
                            <svg width="100" height="100" viewBox="0 0 100 100">
                                <path d="M10 80 Q 40 10, 90 20" fill="none" stroke="currentColor" strokeWidth="2" />
                            </svg>
                        </div>
                        {/* Mock Chart Data for MVP - Ideally passed from Backend or Ledger */}
                        <PnLChart data={[10000, 10000 + stats.metrics.total_pnl / 2, 10000 + stats.metrics.total_pnl]} />
                    </div>

                    <LedgerAudit agentId={id as string} />
                </div>
            </div>
        </div>
    );
}
