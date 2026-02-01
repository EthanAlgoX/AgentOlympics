"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface LineageNode {
    agent_id: string;
    persona: string;
    generation: number;
    parent_id: string | null;
    created_at: string;
}

export default function EvolutionLineage() {
    const [lineage, setLineage] = useState<LineageNode[]>([]);
    const [targetId, setTargetId] = useState("");
    const [loading, setLoading] = useState(false);

    const fetchLineage = async (id: string) => {
        setLoading(true);
        try {
            const res = await fetch(`http://localhost:8000/api/evolution/lineage/${id}`);
            const data = await res.json();
            setLineage(data);
        } catch (err) {
            console.error("Failed to fetch lineage", err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container mx-auto px-6 py-12">
            <div className="mb-12">
                <h2 className="text-4xl font-bold mb-4 glow-text">Strategy Genealogy</h2>
                <p className="text-white/50 max-w-2xl">
                    Trace the evolution of algorithmic strategies. See how mutation and selection drive performance improvements across generations.
                </p>
            </div>

            <div className="flex gap-4 mb-12">
                <input
                    type="text"
                    placeholder="Enter Agent ID (e.g. agent_trend_test)"
                    className="flex-1 bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-blue-500 transition-colors"
                    value={targetId}
                    onChange={(e) => setTargetId(e.target.value)}
                />
                <button
                    onClick={() => fetchLineage(targetId)}
                    className="px-6 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-bold transition-all"
                >
                    Trace Lineage
                </button>
            </div>

            <div className="relative">
                {lineage.length > 0 && (
                    <div className="space-y-8 relative">
                        {lineage.map((node, index) => (
                            <div key={node.agent_id} className="relative flex items-center gap-8">
                                {/* Connector line */}
                                {index < lineage.length - 1 && (
                                    <div className="absolute left-6 top-12 w-0.5 h-12 bg-gradient-to-b from-blue-500 to-transparent"></div>
                                )}

                                <div className="w-12 h-12 rounded-full bg-blue-500/20 border border-blue-500/50 flex items-center justify-center font-bold text-blue-400 z-10 shrink-0">
                                    G{node.generation}
                                </div>

                                <div className="glass-card p-6 flex-1 hover:border-blue-500/30 transition-all group">
                                    <div className="flex justify-between items-start mb-2">
                                        <h4 className="font-mono font-bold text-blue-400">{node.agent_id}</h4>
                                        <span className="text-[10px] text-white/20">{new Date(node.created_at).toLocaleString()}</span>
                                    </div>
                                    <p className="text-sm text-white/60 font-light mb-4">{node.persona}</p>
                                    <Link
                                        href={`/agents/${node.agent_id}`}
                                        className="text-xs font-bold text-white/30 group-hover:text-white transition-colors flex items-center gap-1"
                                    >
                                        View Performance →
                                    </Link>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {!loading && lineage.length === 0 && targetId && (
                    <div className="text-center py-20 bg-white/5 rounded-2xl border border-dashed border-white/10">
                        <p className="text-white/30 italic">No lineage data found for this ID.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
