"use client";

import { useEffect, useState } from "react";
import PnLChart from "@/components/PnLChart";

export default function DuelArena() {
    const [duel, setDuel] = useState<any>(null);

    return (
        <div className="container mx-auto px-6 py-12">
            <div className="mb-12 text-center">
                <h2 className="text-5xl font-black text-white italic tracking-tighter uppercase mb-2">Battle Arena</h2>
                <div className="h-1 w-24 bg-red-600 mx-auto"></div>
                <p className="text-white/40 mt-4 font-mono text-xs uppercase tracking-[0.2em]">Zero-Sum Algorithmic Warfare</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-px bg-white/10 rounded-2xl overflow-hidden border border-white/10 shadow-2xl">
                {/* Left Side: Challenger 1 */}
                <div className="p-12 bg-black/40 relative">
                    <div className="absolute top-4 left-4 text-[10px] font-bold text-red-500 uppercase tracking-widest px-2 py-0.5 border border-red-500/30 rounded">Challenger A</div>
                    <div className="text-center space-y-6">
                        <div className="w-24 h-24 bg-red-500/20 rounded-full mx-auto border-2 border-red-500/40 flex items-center justify-center text-4xl shadow-[0_0_30px_rgba(239,68,68,0.2)]">⚔️</div>
                        <h3 className="text-3xl font-mono font-bold text-red-400">trend_agent_v7</h3>
                        <p className="text-white/40 italic text-sm">"Aggressive momentum capture strategy."</p>
                        <div className="pt-8">
                            <PnLChart data={[10000, 10500, 10300, 10800, 10700]} />
                        </div>
                        <div className="pt-12">
                            <div className="text-[10px] text-white/30 uppercase font-bold mb-4">Last Decision</div>
                            <div className="bg-red-500/10 border border-red-500/30 p-4 rounded-xl font-mono text-sm text-red-400">OPEN LONG ($3,000)</div>
                        </div>
                    </div>
                </div>

                {/* Right Side: Challenger 2 */}
                <div className="p-12 bg-black/40 relative border-l border-white/10">
                    <div className="absolute top-4 right-4 text-[10px] font-bold text-blue-500 uppercase tracking-widest px-2 py-0.5 border border-blue-500/30 rounded">Challenger B</div>
                    <div className="text-center space-y-6">
                        <div className="w-24 h-24 bg-blue-500/20 rounded-full mx-auto border-2 border-blue-500/40 flex items-center justify-center text-4xl shadow-[0_0_30px_rgba(59,130,246,0.2)]">🛡️</div>
                        <h3 className="text-3xl font-mono font-bold text-blue-400">stable_alpha_mutated</h3>
                        <p className="text-white/40 italic text-sm">"Mean-reversion specialist with tail risk hedge."</p>
                        <div className="pt-8">
                            <PnLChart data={[10000, 9800, 10100, 10050, 10150]} />
                        </div>
                        <div className="pt-12">
                            <div className="text-[10px] text-white/30 uppercase font-bold mb-4">Last Decision</div>
                            <div className="bg-blue-500/10 border border-blue-500/30 p-4 rounded-xl font-mono text-sm text-blue-400">OPEN SHORT ($1,500)</div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="glass-card p-8 border-b-4 border-b-red-600/50">
                    <h4 className="text-xs font-bold text-white/40 uppercase mb-4 tracking-widest">A's Advantage</h4>
                    <p className="text-2xl font-mono font-bold text-white">+4.2%</p>
                </div>
                <div className="glass-card p-8 flex items-center justify-center">
                    <div className="text-center">
                        <div className="text-[10px] text-white/30 uppercase font-bold mb-1">Current Pot</div>
                        <div className="text-4xl font-black text-white font-mono">$5,000</div>
                    </div>
                </div>
                <div className="glass-card p-8 border-b-4 border-b-blue-600/50">
                    <h4 className="text-xs font-bold text-white/40 uppercase mb-4 tracking-widest">B's Alpha</h4>
                    <p className="text-2xl font-mono font-bold text-white">-1.5%</p>
                </div>
            </div>
        </div>
    );
}
