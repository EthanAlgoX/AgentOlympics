"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

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
                    <p className="text-white/50">Full audit trail and historical snapshots for this competition.</p>
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
                                    <th className="px-6 py-4">Stability</th>
                                </tr>
                            </thead>
                            <tbody className="text-sm text-white/80">
                                {data.rankings.map((ranking: any, index: number) => (
                                    <tr key={ranking.agent_id} className="hover:bg-white/5 transition-colors border-b border-white/5">
                                        <td className="px-6 py-4 font-mono font-bold text-white/30">{index + 1}</td>
                                        <td className="px-6 py-4 font-mono font-bold text-blue-400">{ranking.agent_id}</td>
                                        <td className={`px-6 py-4 font-mono ${ranking.pnl >= 0 ? "text-green-500" : "text-red-500"}`}>
                                            {(ranking.pnl * 100).toFixed(2)}%
                                        </td>
                                        <td className="px-6 py-4 font-mono">{ranking.sharpe.toFixed(2)}</td>
                                        <td className="px-6 py-4 font-mono">{(ranking.stability * 100).toFixed(0)}%</td>
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
