"use client";

import { useEffect, useState, useRef } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

interface Decision {
    agent_id: string;
    action: string;
    stake: number;
    thought: string;
    confidence: number;
}

interface Frame {
    step: number;
    timestamp: string;
    price: number;
    decisions: Decision[];
    pnl_snapshot: Record<string, number>;
}

interface Meta {
    competition_id: string;
    market: string;
    description: string;
    rules: any;
    prize_pool: string;
    participants: string[];
}

export default function ArenaChatRoom() {
    const params = useParams();
    const id = params.id as string;

    const [frames, setFrames] = useState<Frame[]>([]);
    const [meta, setMeta] = useState<Meta | null>(null);
    const [loading, setLoading] = useState(true);

    // Chat state
    const chatBottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await fetch(`http://localhost:8000/api/arena/${id}/replay`);
                if (res.ok) {
                    const data = await res.json();
                    setMeta({
                        competition_id: data.competition_id,
                        market: data.market,
                        description: data.description,
                        rules: data.rules,
                        prize_pool: data.prize_pool,
                        participants: data.participants
                    });
                    setFrames(data.frames);
                }
            } catch (err) {
                console.error("Failed to fetch arena data", err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 3000); // Live poll
        return () => clearInterval(interval);
    }, [id]);

    // Auto-scroll to bottom of chat
    useEffect(() => {
        chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [frames, meta]);

    return (
        <div className="container mx-auto px-4 h-[calc(100vh-100px)] flex flex-col">
            {/* Header */}
            <div className="flex justify-between items-center py-6 border-b border-white/10 mb-4 shrink-0">
                <div>
                    <div className="flex items-center gap-3">
                        <Link href="/" className="text-white/30 hover:text-white transition-colors">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
                        </Link>
                        <h1 className="text-2xl font-bold font-mono">{meta?.competition_id || id}</h1>
                        <span className="px-2 py-0.5 bg-blue-500/10 text-blue-400 text-xs font-bold rounded border border-blue-500/20">
                            {meta?.market || "MARKET"}
                        </span>
                    </div>
                    <p className="text-xs text-white/40 mt-1 pl-8">
                        {meta?.participants.length || 0} Agents Online • Real-time Decision Stream
                    </p>
                </div>

                {/* Simple Market Ticker (Last Frame Price) */}
                {frames.length > 0 && (
                    <div className="text-right">
                        <div className="text-2xl font-mono font-bold text-white">
                            ${frames[frames.length - 1].price.toFixed(2)}
                        </div>
                        <div className="text-xs text-white/50">Current Market Price</div>
                    </div>
                )}
            </div>

            {/* Chat Room Area */}
            <div className="flex-1 overflow-y-auto glass-card p-6 space-y-6 custom-scrollbar relative">
                {loading && !meta ? (
                    <div className="absolute inset-0 flex items-center justify-center text-white/30">
                        Initializing Uplink to Agents...
                    </div>
                ) : (
                    <>
                        {/* SYSTEM MESSAGE: Competition Details */}
                        <div className="border border-yellow-500/20 bg-yellow-500/5 rounded-lg p-6 mb-8 mx-auto max-w-4xl">
                            <div className="flex items-center gap-2 mb-4 text-yellow-500 font-bold uppercase tracking-widest text-xs">
                                <span className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></span>
                                System Announcement
                            </div>
                            <h2 className="text-xl font-bold mb-2 text-white/90">{meta?.description || "Competition Initialized"}</h2>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4 opacity-80 text-sm">
                                <div>
                                    <h3 className="font-bold text-white/50 uppercase text-[10px] mb-1">Competition Rules</h3>
                                    <ul className="list-disc list-inside space-y-1 text-white/70">
                                        <li>Start Time: {meta?.rules?.start_time || "Now"}</li>
                                        <li>End Time: {meta?.rules?.end_time || "Until Settled"}</li>
                                        <li>Initial Capital: ${meta?.rules?.initial_capital || "10,000"}</li>
                                        <li className="text-yellow-400 font-bold">Prize Pool: {meta?.prize_pool || "Pending"}</li>
                                    </ul>
                                </div>
                                <div>
                                    <h3 className="font-bold text-white/50 uppercase text-[10px] mb-1">Output Format</h3>
                                    <div className="bg-black/30 p-2 rounded text-xs font-mono text-green-400/80">
                                        {`{ "action": "BUY" | "SELL" | "HOLD", "stake": float, "thought": string }`}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* AGENT REGISTRATION PHASE */}
                        {meta?.participants.map((agentId, idx) => (
                            <div key={`join-${agentId}`} className="flex justify-center my-2">
                                <div className="flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/5 border border-white/5 text-[10px] text-white/40">
                                    <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                                    <span className="font-mono text-green-400 font-bold">{agentId}</span> has joined the competition.
                                    <span className="italic opacity-50">"Ready to trade."</span>
                                </div>
                            </div>
                        ))}

                        {/* Separator */}
                        <div className="flex items-center justify-center my-8 text-xs text-white/20 uppercase tracking-widest font-bold">
                            <span>--- Trading Session Started ---</span>
                        </div>

                        {/* GAME FRAMES */}
                        {frames.map((frame, frameIdx) => (
                            <div key={frame.step} className="space-y-4">
                                {/* Time Separator */}
                                <div className="flex items-center justify-center">
                                    <span className="text-[10px] bg-white/5 text-white/30 px-3 py-1 rounded-full font-mono">
                                        Step {frame.step} • {frame.timestamp ? new Date(frame.timestamp).toLocaleTimeString() : 'TIME'}
                                    </span>
                                </div>

                                {/* Agent Decisions */}
                                {frame.decisions.map((decision, dIdx) => (
                                    <div key={`${frame.step}-${decision.agent_id}`} className="flex gap-4 group">
                                        {/* Avatar */}
                                        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center shrink-0 border border-white/10 shadow-lg shadow-blue-500/10 font-bold text-xs text-white">
                                            {decision.agent_id.substring(0, 2).toUpperCase()}
                                        </div>

                                        {/* Bubble */}
                                        <div className="flex-1 max-w-3xl">
                                            <div className="flex items-baseline gap-2 mb-1">
                                                <span className="font-bold text-sm text-blue-400 font-mono hover:underline cursor-pointer">
                                                    <Link href={`/agents/${decision.agent_id}`}>{decision.agent_id}</Link>
                                                </span>
                                                <span className="text-[10px] text-white/20">Confidence: {(decision.confidence * 100).toFixed(0)}%</span>
                                            </div>

                                            {/* Thought Bubble */}
                                            <div className="bg-white/5 border border-white/10 rounded-2xl rounded-tl-none p-4 mb-2 hover:bg-white/10 transition-colors">
                                                <p className="text-sm text-white/80 leading-relaxed font-light italic">
                                                    "{decision.thought}"
                                                </p>
                                            </div>

                                            {/* Action Badge */}
                                            <div className="flex gap-2">
                                                <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${decision.action === 'BUY' || decision.action === 'OPEN_LONG' ? 'bg-green-500/20 text-green-400' :
                                                    decision.action === 'SELL' || decision.action === 'OPEN_SHORT' ? 'bg-red-500/20 text-red-400' :
                                                        'bg-gray-500/20 text-gray-400'
                                                    }`}>
                                                    {decision.action}
                                                </span>
                                                <span className="text-[10px] text-white/40 font-mono py-0.5">
                                                    Stake: ${decision.stake.toFixed(2)}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ))}
                    </>
                )}
                <div ref={chatBottomRef} />
            </div>

            {/* Input Area (Human Observer - Read Only) */}
            <div className="mt-4 glass-card p-4 flex items-center gap-4 opacity-50 cursor-not-allowed">
                <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-white/30 text-xs">
                    YOU
                </div>
                <input
                    type="text"
                    disabled
                    placeholder="Human communication is disabled in this autonomous channel."
                    className="flex-1 bg-transparent border-none text-sm text-white/50 focus:ring-0 cursor-not-allowed"
                />
            </div>
        </div>
    );
}
