"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

export default function LeaderboardDetail() {
    const { id } = useParams();
    const [data, setData] = useState<any>(null);

    useEffect(() => {
        fetch(`http://localhost:8000/api/leaderboard/${id}`)
            .then(res => res.json())
            .then(d => setData(d));
    }, [id]);

    if (!data) return <div className="p-20 text-center">Loading Competition Data...</div>;

    return (
        <div className="container mx-auto px-6">
            <div className="mb-12 flex justify-between items-end">
                <div>
                    <h2 className="text-4xl font-bold glow-text mb-2 uppercase">{data.competition_id}</h2>
                    <div className="flex items-center gap-4">
                        <p className="text-white/50">Full audit trail and historical snapshots.</p>
                        <div className="flex items-center gap-1">
                            {['CREATED', 'OPEN_FOR_REGISTRATION', 'DECISION_FROZEN', 'SETTLED'].map((s, i) => (
                                <div key={s} className="flex items-center">
                                    <div className={`h-1.5 w-12 rounded-full ${data.status === s ? 'bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.5)]' :
                                        (['SETTLED', 'ARCHIVED'].includes(data.status) || (data.status === 'DECISION_FROZEN' && i < 2)) ? 'bg-blue-900/40' : 'bg-white/5'
                                        }`}></div>
                                    {i < 3 && <div className="text-[10px] text-white/10 mx-1">/</div>}
                                </div>
                            ))}
                        </div>
                        <span className="text-[10px] font-mono text-blue-400 font-bold uppercase tracking-widest">{data.status}</span>
                    </div>
                </div>
                <div className="text-right">
                    <div className="text-xs text-white/30 uppercase font-bold mb-1">Last Updated</div>
                    <div className="text-sm font-mono">{new Date(data.snapshot_at).toLocaleString()}</div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                <div className="lg:col-span-3">
                    <div className="glass-card overflow-hidden">
                        <table className="w-full text-left">
                            <thead className="border-b border-white/10 text-xs uppercase text-white/30 font-bold">
                                <tr>
                                    <th className="px-6 py-4">Rank</th>
                                    <th className="px-6 py-4">Agent</th>
                                    <th className="px-6 py-4">PnL</th>
                                    <th className="px-6 py-4">Sharpe</th>
                                    <th className="px-6 py-4">Max DD</th>
                                </tr>
                            </thead>
                            <tbody className="text-sm text-white/80">
                                {data.rankings.map((ranking: any, index: number) => (
                                    <tr key={ranking.agent_id} className="hover:bg-white/5 transition-colors border-b border-white/5">
                                        <td className="px-6 py-4 font-mono font-bold text-white/30">{index + 1}</td>
                                        <td className="px-6 py-4 font-mono font-bold text-blue-400">
                                            <Link href={`/agents/${ranking.agent_id}`} className="hover:underline">
                                                {ranking.agent_id}
                                            </Link>
                                        </td>
                                        <td className={`px-6 py-4 font-mono ${ranking.pnl >= 0 ? "text-green-500" : "text-red-500"}`}>
                                            ${ranking.pnl.toFixed(2)}
                                        </td>
                                        <td className="px-6 py-4 font-mono text-white/60">{ranking.sharpe.toFixed(2)}</td>
                                        <td className="px-6 py-4 font-mono text-red-400">{(ranking.max_dd * 100).toFixed(1)}%</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
                <div className="space-y-6">
                    <div className="glass-card p-6">
                        <h4 className="font-bold mb-4 text-xs uppercase text-white/30">Competition Rules</h4>
                        <div className="space-y-3 text-sm">
                            <div className="flex justify-between">
                                <span className="text-white/50">Initial Cash</span>
                                <span>$100,000</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-white/50">Market</span>
                                <span>BTC/USDT</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-white/50">Interval</span>
                                <span>1 Hour</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
