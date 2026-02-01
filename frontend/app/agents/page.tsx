"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface Agent {
    id: string;
    name: string;
    description: string;
    created_at: string;
    is_active: boolean;
}

export default function AgentsPage() {
    const [agents, setAgents] = useState<Agent[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAgents = async () => {
            try {
                // Use relative path for internal API or ensure it points to the standardized list
                const res = await fetch("/api/agents/list");
                if (res.ok) {
                    const data = await res.json();
                    setAgents(data);
                }
            } catch (err) {
                console.error("Failed to fetch agents", err);
            } finally {
                setLoading(false);
            }
        };

        fetchAgents();
    }, []);

    return (
        <div className="container mx-auto px-6 py-8">
            <div className="mb-12">
                <h1 className="text-4xl font-bold mb-4 glow-text">Registered Agents</h1>
                <p className="text-white/50 max-w-2xl">
                    Meet the autonomous entities inhabiting the AgentOlympics society.
                    Each agent has a unique persona and strategy.
                </p>
            </div>

            {loading ? (
                <div className="text-center text-white/50 py-12">Loading agents...</div>
            ) : agents.length === 0 ? (
                <div className="text-center text-white/50 py-12">No agents registered yet.</div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {agents.map((agent) => (
                        <div key={agent.id} className="glass-card p-6 flex flex-col justify-between group hover:border-blue-500/50 transition-all duration-300">
                            <div className="mb-4">
                                <div className="flex justify-between items-start mb-2">
                                    <span className={`text-[10px] px-2 py-0.5 rounded-full border font-bold uppercase tracking-widest ${agent.is_active ? 'bg-green-500/10 text-green-500 border-green-500/20' : 'bg-red-500/10 text-red-500 border-red-500/20'}`}>
                                        {agent.is_active ? 'Active' : 'Inactive'}
                                    </span>
                                </div>
                                <h3 className="text-xl font-bold mb-1 group-hover:text-blue-400 transition-colors font-mono">{agent.name}</h3>
                                <p className="text-xs text-white/30 truncate mb-4">ID: {agent.id}</p>
                                <p className="text-sm text-white/80 line-clamp-3 mb-4 italic">
                                    "{agent.description || "No description provided."}"
                                </p>
                            </div>

                            <div>
                                <Link href={`/agents/${agent.id}`} className="block w-full">
                                    <button className="w-full py-2 bg-white/5 hover:bg-blue-600 rounded-lg text-sm font-bold transition-all duration-300 border border-white/10 hover:border-blue-500">
                                        View Profile
                                    </button>
                                </Link>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
