import React from 'react';

interface Competition {
    slug: string;
    title: string;
    status: string;
    pool: string;
    participants: number;
    market: string;
    start_time?: string;
    lock_time?: string;
    duration_minutes?: number;
}

interface CompetitionInfoProps {
    comp: Competition;
    topAgents?: any[]; // Passed from parent or fetched
}

export default function CompetitionInfo({ comp, topAgents = [] }: CompetitionInfoProps) {
    // Calculate elapsed time (mock or real if start_time exists)
    // For demo, we just show a static or simple timer if we had start_time.
    // User requested "Elapsed: 00:41". 

    return (
        <div className="h-full flex flex-col justify-between">
            {/* Header / Meta */}
            <div>
                <div className="flex justify-between items-start mb-4">
                    <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60">
                        {comp.title}
                    </h2>
                    <span className="px-2 py-1 bg-green-500/10 text-green-400 border border-green-500/20 text-xs font-bold rounded uppercase tracking-widest animate-pulse">
                        LIVE
                    </span>
                </div>

                <div className="grid grid-cols-2 gap-y-2 gap-x-4 text-sm mb-6 border-b border-white/10 pb-6">
                    <div className="flex flex-col">
                        <span className="text-white/40 text-xs uppercase tracking-wider">Market</span>
                        <span className="font-mono text-blue-300 font-bold">{comp.market}</span>
                    </div>
                    <div className="flex flex-col">
                        <span className="text-white/40 text-xs uppercase tracking-wider">Prize</span>
                        <span className="font-mono text-yellow-400 font-bold">{comp.pool}</span>
                    </div>
                    <div className="flex flex-col">
                        <span className="text-white/40 text-xs uppercase tracking-wider">Agents</span>
                        <span className="font-mono text-white/80">{comp.participants} Connected</span>
                    </div>
                </div>
            </div>

            {/* Leaderboard (Mini) */}
            <div className="mb-6 flex-1">
                <h3 className="text-xs uppercase font-bold text-white/30 mb-3 tracking-widest">
                    Top Positions
                </h3>
                <div className="space-y-2">
                    {topAgents.slice(0, 3).map((agent, idx) => (
                        <div key={agent.agent_id} className="flex justify-between items-center text-sm p-2 rounded hover:bg-white/5 border border-transparent hover:border-white/5 transition-colors">
                            <div className="flex items-center gap-3">
                                <span className={`font-mono font-bold w-4 text-center ${idx === 0 ? 'text-yellow-400' : 'text-white/40'}`}>
                                    {idx + 1}
                                </span>
                                <span className="font-bold text-blue-400">{agent.agent_name || agent.agent_id}</span>
                            </div>
                            <span className={`font-mono font-bold ${agent.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                {agent.pnl > 0 ? '+' : ''}{agent.pnl.toFixed(1)}%
                            </span>
                        </div>
                    ))}
                    {topAgents.length === 0 && (
                        <div className="text-white/20 text-xs italic p-2">Waiting for positions...</div>
                    )}
                </div>
            </div>

            {/* System Signals (Static/Mocked for MVP as requested) */}
            <div className="bg-black/20 rounded p-3 border border-white/5">
                <h3 className="text-[10px] uppercase font-bold text-white/30 mb-2 tracking-widest">
                    System Signals
                </h3>
                <div className="grid grid-cols-3 gap-2 text-xs">
                    <div>
                        <span className="block text-white/30 text-[9px]">Volatility</span>
                        <span className="text-red-400 font-bold">HIGH</span>
                    </div>
                    <div>
                        <span className="block text-white/30 text-[9px]">Funding</span>
                        <span className="text-green-400 font-bold">POSITIVE</span>
                    </div>
                    <div>
                        <span className="block text-white/30 text-[9px]">Latency</span>
                        <span className="text-blue-400 font-bold">42ms</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
