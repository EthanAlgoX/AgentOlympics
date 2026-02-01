"use client";

import { useState } from "react";

export default function SubmitAgent() {
    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState({
        name: "",
        description: "",
        code: "def decide(context, market_data):\n    return {'action': 'WAIT', 'stake': 0}\n",
        author: "Ethan",
        version: "1.0.0"
    });
    const [status, setStatus] = useState<any>(null);

    const handleSubmit = async () => {
        setStep(3);
        setStatus({ message: "Auditing submission...", type: "info" });

        try {
            const res = await fetch("/api/evolution/submit", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    agent_id: formData.name.toLowerCase().replace(/\s/g, "_"),
                    owner_user: formData.author,
                    code: formData.code,
                    manifest: {
                        agent_name: formData.name,
                        author: formData.author,
                        version: formData.version,
                        description: formData.description,
                        entrypoint: "strategy.py"
                    }
                })
            });
            const data = await res.json();
            if (data.status === "success") {
                setStatus({ message: "Verification Passed! Agent is now live.", type: "success" });
            } else {
                setStatus({ message: `Verification Failed: ${data.detail}`, type: "error" });
            }
        } catch (err) {
            setStatus({ message: "Network error during submission.", type: "error" });
        }
    };

    return (
        <div className="container mx-auto px-6 py-12 max-w-4xl">
            <div className="mb-12">
                <h2 className="text-4xl font-black text-white italic tracking-tighter uppercase mb-2">Submit Your Olympian</h2>
                <div className="h-1 w-24 bg-blue-600"></div>
            </div>

            <div className="glass-card p-12 space-y-8">
                {step === 1 && (
                    <div className="space-y-6 animate-in fade-in duration-500">
                        <h3 className="text-xl font-bold text-white/90">Step 1: Identity & Meta</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            <div className="space-y-2">
                                <label className="text-[10px] font-bold text-white/40 uppercase tracking-widest">Agent Name</label>
                                <input
                                    className="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-white focus:border-blue-500/50 transition-all outline-none"
                                    placeholder="e.g. TrendFinderPro"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-[10px] font-bold text-white/40 uppercase tracking-widest">Version</label>
                                <input
                                    className="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-white outline-none"
                                    value={formData.version}
                                    onChange={(e) => setFormData({ ...formData, version: e.target.value })}
                                />
                            </div>
                        </div>
                        <div className="space-y-2">
                            <label className="text-[10px] font-bold text-white/40 uppercase tracking-widest">Strategy Description</label>
                            <textarea
                                rows={4}
                                className="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-white outline-none focus:border-blue-500/50"
                                placeholder="Explain the logic behind this agent..."
                                value={formData.description}
                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                            />
                        </div>
                        <button
                            onClick={() => setStep(2)}
                            className="w-full py-5 bg-blue-600 hover:bg-blue-500 text-white font-black uppercase tracking-widest rounded-xl transition-all shadow-[0_10px_30px_rgba(37,99,235,0.3)]"
                        >
                            Next: Code Upload
                        </button>
                    </div>
                )}

                {step === 2 && (
                    <div className="space-y-6 animate-in slide-in-from-right duration-500">
                        <div className="flex justify-between items-center">
                            <h3 className="text-xl font-bold text-white/90">Step 2: Strategy Definition</h3>
                            <button onClick={() => setStep(1)} className="text-[10px] text-white/40 hover:text-white uppercase font-bold">Back</button>
                        </div>
                        <div className="space-y-2">
                            <label className="text-[10px] font-bold text-white/40 uppercase tracking-widest">Code (Python)</label>
                            <textarea
                                rows={12}
                                className="w-full bg-black/60 border border-white/10 rounded-xl p-6 text-blue-300 font-mono text-sm outline-none"
                                value={formData.code}
                                onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                            />
                        </div>
                        <button
                            onClick={handleSubmit}
                            className="w-full py-5 bg-blue-600 hover:bg-blue-500 text-white font-black uppercase tracking-widest rounded-xl transition-all shadow-[0_10px_30px_rgba(37,99,235,0.3)]"
                        >
                            Finalize & Audit
                        </button>
                    </div>
                )}

                {step === 3 && (
                    <div className="text-center py-20 animate-in zoom-in duration-500">
                        <div className={`text-4xl mb-6 ${status?.type === 'error' ? 'text-red-500' : 'text-blue-500'}`}>
                            {status?.type === 'info' && <div className="animate-spin inline-block w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full"></div>}
                            {status?.type === 'success' && "✅"}
                            {status?.type === 'error' && "❌"}
                        </div>
                        <h3 className="text-2xl font-black text-white uppercase italic">{status?.message}</h3>
                        {status?.type === 'success' && (
                            <button onClick={() => window.location.href = '/leaderboard'} className="mt-12 px-12 py-4 bg-white text-black font-black uppercase tracking-widest rounded-full hover:bg-white/90 transition-all">Go to Leaderboard</button>
                        )}
                        {status?.type === 'error' && (
                            <button onClick={() => setStep(2)} className="mt-12 px-12 py-4 border border-white/20 text-white/40 font-bold uppercase tracking-widest rounded-full hover:text-white transition-all">Fix Code</button>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
