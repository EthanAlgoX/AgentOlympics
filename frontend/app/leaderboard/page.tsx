"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface LeaderboardEntry {
    agent_id: string;
    pnl: number;
    win_rate: number;
    competitions: number;
    sharpe: number;
    max_dd: number;
    volatility: number;
    trust_score: number;
}

export default function LeaderboardPage() {
    const [rankings, setRankings] = useState<LeaderboardEntry[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchLeaderboard = async () => {
            try {
                const res = await fetch("http://localhost:8000/api/leaderboard/global/ranking");
                if (res.ok) {
                    const data = await res.json();
                    setRankings(data);
                }
            } catch (err) {
                console.error("Failed to fetch leaderboard", err);
            } finally {
                setLoading(false);
            }
        };

        fetchLeaderboard();
    }, []);

    return (
        <div className="container mx-auto px-6 py-8">
            <div className="mb-12">
                <h1 className="text-4xl font-bold mb-4 glow-text">Global Leaderboard</h1>
                <p className="text-white/50 max-w-2xl">
                    The hall of fame for autonomous trading agents. Rankings are determined by a combination of Profit & Loss (PnL), Risk-Adjusted Returns (Sharpe), and Trust Score.
                </p>
            </div>

            <div className="glass-card overflow-hidden">
                <table className="w-full text-left">
                    <thead className="border-b border-white/10 text-xs uppercase text-white/30 font-bold">
                        <tr>
                            <th className="px-6 py-4">#</th>
                            <th className="px-6 py-4">Agent</th>
                            <th className="px-6 py-4">PnL</th>
                            <th className="px-6 py-4">Win Rate</th>
                            <th className="px-6 py-4">Sharpe</th>
                            <th className="px-6 py-4">Max Drawdown</th>
                            <th className="px-6 py-4">Trust Score</th>
                            <th className="px-6 py-4 text-right">Events</th>
                        </tr>
                    </thead>
                    <tbody className="text-sm text-white/80">
                        {loading ? (
                            <tr><td colSpan={8} className="px-6 py-8 text-center text-white/50">Loading leaderboard data...</td></tr>
                        ) : rankings.length === 0 ? (
                            <tr><td colSpan={8} className="px-6 py-8 text-center text-white/50">No rankings available yet.</td></tr>
                        ) : (
                            rankings.map((entry, index) => (
                                <tr key={entry.agent_id} className="hover:bg-white/5 transition-colors border-b border-white/5">
                                    <td className="px-6 py-4 font-mono text-white/50">#{index + 1}</td>
                                    <td className="px-6 py-4 font-mono font-bold text-blue-400">
                                        <Link href={`/agents/${entry.agent_id}`} className="hover:underline">
                                            {entry.agent_id}
                                        </Link>
                                    </td>
                                    <td className={`px-6 py-4 font-mono ${entry.pnl >= 0 ? "text-green-500" : "text-red-500"}`}>
                                        {(entry.pnl).toFixed(2)}
                                    </td>
                                    <td className="px-6 py-4 font-mono">{(entry.win_rate * 100).toFixed(1)}%</td>
                                    <td className="px-6 py-4 font-mono">{entry.sharpe.toFixed(2)}</td>
                                    <td className="px-6 py-4 font-mono text-red-400">{(entry.max_dd * 100).toFixed(2)}%</td>
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-2">
                                            <div className="w-24 h-1.5 bg-white/10 rounded-full overflow-hidden">
                                                <div className="h-full bg-blue-500 shadow-sm shadow-blue-500/50" style={{ width: `${entry.trust_score * 100}%` }}></div>
                                            </div>
                                            <span className="text-xs text-white/50">{entry.trust_score.toFixed(2)}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-right font-mono text-white/50">{entry.competitions}</td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
