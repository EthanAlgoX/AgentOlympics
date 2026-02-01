"use client";

import { useEffect, useState } from "react";

interface LedgerEvent {
    id: number;
    competition_id: string;
    event_type: string;
    amount: number;
    balance_after: number;
    timestamp: string;
}

export default function LedgerAudit({ agentId }: { agentId: string }) {
    const [events, setEvents] = useState<LedgerEvent[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchLedger = async () => {
            try {
                const res = await fetch(`http://localhost:8000/api/evolution/ledger/${agentId}`);
                const data = await res.json();
                setEvents(data);
            } catch (err) {
                console.error("Failed to fetch ledger", err);
            } finally {
                setLoading(false);
            }
        };
        fetchLedger();
    }, [agentId]);

    if (loading) return <div className="animate-pulse text-white/20 text-xs">Auditing ledger...</div>;

    return (
        <div className="glass-card overflow-hidden">
            <div className="p-4 border-b border-white/10 flex justify-between items-center bg-white/5">
                <h3 className="text-sm font-bold uppercase tracking-wider text-white/70">Ledger Audit Log</h3>
                <span className="text-[10px] bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded-full border border-blue-500/30">Immutable</span>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                    <thead>
                        <tr className="bg-white/5 text-white/40">
                            <th className="p-3 font-medium">Time</th>
                            <th className="p-3 font-medium">Type</th>
                            <th className="p-3 font-medium">Competition</th>
                            <th className="p-3 font-medium text-right">Amount</th>
                            <th className="p-3 font-medium text-right">Balance</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {events.map((event) => (
                            <tr key={event.id} className="hover:bg-white/[0.02] transition-colors">
                                <td className="p-3 text-white/30">{new Date(event.timestamp).toLocaleString()}</td>
                                <td className="p-3">
                                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${event.event_type === 'SETTLE' ? 'bg-green-500/20 text-green-400' :
                                            event.event_type === 'LOCK' ? 'bg-orange-500/20 text-orange-400' :
                                                'bg-white/10 text-white/50'
                                        }`}>
                                        {event.event_type}
                                    </span>
                                </td>
                                <td className="p-3 font-mono text-white/50">{event.competition_id}</td>
                                <td className={`p-3 text-right font-bold ${event.amount >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                    {event.amount >= 0 ? '+' : ''}{event.amount.toFixed(2)}
                                </td>
                                <td className="p-3 text-right text-white font-mono">{event.balance_after.toFixed(2)}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
