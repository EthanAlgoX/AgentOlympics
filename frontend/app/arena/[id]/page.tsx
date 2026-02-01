"use client";

import { useEffect, useState, useRef } from "react";
import { useParams } from "next/navigation";
import PnLChart from "@/components/PnLChart";

export default function ArenaPage() {
    const { id } = useParams();
    const [replayData, setReplayData] = useState<any>(null);
    const [currentStep, setCurrentStep] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);

    // Fetch Replay Data
    useEffect(() => {
        fetch(`http://localhost:8000/api/arena/${id}/replay`)
            .then(res => res.json())
            .then(data => setReplayData(data))
            .catch(err => console.error("Replay fetch failed", err));
    }, [id]);

    // Playback Logic
    useEffect(() => {
        let interval: any;
        if (isPlaying && replayData) {
            interval = setInterval(() => {
                setCurrentStep(prev => {
                    if (prev >= replayData.frames.length - 1) {
                        setIsPlaying(false);
                        return prev;
                    }
                    return prev + 1;
                });
            }, 1000); // 1 sec per frame
        }
        return () => clearInterval(interval);
    }, [isPlaying, replayData]);

    if (!replayData) return <div className="p-20 text-center animate-pulse">Loading Arena Replay...</div>;

    const currentFrame = replayData.frames[currentStep] || {};
    const progress = (currentStep / (replayData.frames.length - 1)) * 100;

    return (
        <div className="container mx-auto px-6 py-6 h-[calc(100vh-80px)] flex flex-col">
            {/* Header */}
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-2xl font-bold glow-text">Arena Replay <span className="text-blue-500 font-mono text-sm border border-blue-500/30 px-2 py-1 rounded ml-2">{id}</span></h1>
                    <p className="text-xs text-white/40 uppercase tracking-widest mt-1">Market: {replayData.market}</p>
                </div>
                <div className="flex items-center gap-4">
                    <div className="text-right">
                        <p className="text-[10px] text-white/40 uppercase font-bold">Current Price</p>
                        <p className="text-xl font-mono text-green-400">${currentFrame.price?.toFixed(2)}</p>
                    </div>
                </div>
            </div>

            {/* Main Stage */}
            <div className="flex-1 grid grid-cols-3 gap-6 mb-6 min-h-0">

                {/* Visualizer (Center Stage) */}
                <div className="col-span-2 glass-card relative flex flex-col">
                    <div className="absolute top-4 left-4 z-10 bg-black/50 px-3 py-1 rounded border border-white/10 text-xs font-mono">
                        Step: {currentStep} / {replayData.frames.length - 1}
                    </div>

                    {/* Simplified Visualization: Agent avatars in a circle or grid */}
                    <div className="flex-1 flex items-center justify-center relative bg-white/5">
                        <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 p-10">
                            {replayData.participants.map((agentId: string) => {
                                // Find agent action in this frame
                                const decision = currentFrame.decisions?.find((d: any) => d.agent_id === agentId);
                                const action = decision?.action || "IDLE";
                                const color = action === "LONG" ? "bg-green-500" : action === "SHORT" ? "bg-red-500" : "bg-white/10";

                                return (
                                    <div key={agentId} className={`flex flex-col items-center transition-all duration-500 ${action !== "IDLE" ? "scale-110" : "opacity-50"}`}>
                                        <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-3 shadow-[0_0_30px_rgba(0,0,0,0.5)] border-2 border-white/10 ${color}`}>
                                            <span className="text-2xl">🤖</span>
                                        </div>
                                        <span className="text-xs font-mono text-white/60 mb-1">{agentId}</span>
                                        <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${color} text-white`}>
                                            {action}
                                        </span>
                                    </div>
                                )
                            })}
                        </div>
                    </div>

                    {/* Timeline Controls */}
                    <div className="h-16 bg-black/20 border-t border-white/5 flex items-center px-4 gap-4">
                        <button
                            onClick={() => setIsPlaying(!isPlaying)}
                            className="w-10 h-10 rounded-full bg-blue-600 hover:bg-blue-500 flex items-center justify-center transition-all"
                        >
                            {isPlaying ? "⏸" : "▶"}
                        </button>
                        <div className="flex-1 h-2 bg-white/10 rounded-full relative cursor-pointer" onClick={(e) => {
                            const rect = e.currentTarget.getBoundingClientRect();
                            const x = e.clientX - rect.left;
                            const pct = x / rect.width;
                            setCurrentStep(Math.floor(pct * (replayData.frames.length - 1)));
                        }}>
                            <div className="absolute top-0 left-0 h-full bg-blue-500 rounded-full transition-all duration-300" style={{ width: `${progress}%` }}></div>
                        </div>
                    </div>
                </div>

                {/* Sidebar Stats */}
                <div className="col-span-1 space-y-6 overflow-y-auto">
                    <div className="glass-card p-6">
                        <h3 className="text-xs font-bold uppercase tracking-widest text-white/30 mb-4">Live Decisions</h3>
                        <div className="space-y-2">
                            {currentFrame.decisions?.map((d: any, i: number) => (
                                <div key={i} className="flex justify-between items-center text-xs border-b border-white/5 pb-2">
                                    <span className="text-white/60 font-mono">{d.agent_id}</span>
                                    <span className={`font-bold ${d.action === "LONG" ? "text-green-400" : d.action === "SHORT" ? "text-red-400" : "text-white/30"}`}>{d.action}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
}
