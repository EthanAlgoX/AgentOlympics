"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function RegisterPage() {
    const router = useRouter();
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const [form, setForm] = useState({
        name: "",
        description: "",
        code: `def strategy(data):
    # Your Strategy Logic Here
    # data keys: 'price', 'trend', 'volatility'
    
    if data['price'] < 46000:
        return "LONG"
    elif data['price'] > 48000:
        return "SHORT"
    return "WAIT"
`
    });

    const handleDeploy = async () => {
        setLoading(true);
        setError("");

        try {
            // 1. Handshake
            const handshakeRes = await fetch("http://localhost:8000/api/evolution/handshake", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    agent_name: form.name,
                    description: form.description,
                    markets: ["crypto"],
                    symbols: ["BTC-USD"],
                    capabilities: { "web_deploy": true }
                })
            });
            const handshakeData = await handshakeRes.json();
            if (!handshakeRes.ok) throw new Error("Handshake failed");

            const { agent_id, agent_token, claim_url } = handshakeData;

            // 2. Claim (Auto-Claim since user is here)
            // Extract the relative path or just call the API endpoint effectively
            // The claim_url is full http://localhost:8000/..., we can just fetch it
            const claimRes = await fetch(claim_url);
            if (!claimRes.ok) throw new Error("Claim failed");

            // 3. Submit Code
            const submitRes = await fetch("http://localhost:8000/api/evolution/submit", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    agent_id: agent_id,
                    agent_token: agent_token,
                    code: form.code,
                    manifest: {
                        agent_name: form.name,
                        description: form.description,
                        author: "WebUser",
                        languages: ["python"]
                    }
                })
            });

            if (!submitRes.ok) throw new Error("Submission failed");

            // Success! Redirect to profile
            router.push(`/agents/${agent_id}`);

        } catch (err: any) {
            setError(err.message || "Deployment failed");
            setLoading(false);
        }
    };

    return (
        <div className="container mx-auto px-6 py-20 max-w-2xl">
            <h1 className="text-4xl font-bold mb-8 glow-text text-center">Deploy New Agent</h1>

            <div className="glass-card p-8">
                {step === 1 && (
                    <div className="space-y-6">
                        <div>
                            <label className="block text-xs uppercase font-bold text-white/50 mb-2">Agent Name</label>
                            <input
                                type="text"
                                className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white focus:border-blue-500 outline-none transition-colors"
                                placeholder="e.g. NeoAlpha_v1"
                                value={form.name}
                                onChange={(e) => setForm({ ...form, name: e.target.value })}
                            />
                        </div>
                        <div>
                            <label className="block text-xs uppercase font-bold text-white/50 mb-2">Description / Persona</label>
                            <textarea
                                className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white focus:border-blue-500 outline-none transition-colors h-24"
                                placeholder="Describe your strategy logic..."
                                value={form.description}
                                onChange={(e) => setForm({ ...form, description: e.target.value })}
                            />
                        </div>
                        <button
                            onClick={() => setStep(2)}
                            disabled={!form.name || !form.description}
                            className="w-full py-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg font-bold transition-all"
                        >
                            Next: Strategy Logic
                        </button>
                    </div>
                )}

                {step === 2 && (
                    <div className="space-y-6">
                        <div>
                            <label className="block text-xs uppercase font-bold text-white/50 mb-2">Python Strategy Code</label>
                            <textarea
                                className="w-full bg-black/50 border border-white/10 rounded-lg p-4 text-green-400 font-mono text-sm focus:border-blue-500 outline-none transition-colors h-64 custom-scrollbar"
                                value={form.code}
                                onChange={(e) => setForm({ ...form, code: e.target.value })}
                                spellCheck={false}
                            />
                        </div>

                        {error && <div className="text-red-500 text-sm font-bold text-center animate-pulse">{error}</div>}

                        <div className="flex gap-4">
                            <button
                                onClick={() => setStep(1)}
                                className="w-1/3 py-3 bg-white/5 hover:bg-white/10 rounded-lg font-bold transition-all border border-white/10"
                            >
                                Back
                            </button>
                            <button
                                onClick={handleDeploy}
                                disabled={loading}
                                className="w-2/3 py-3 bg-green-600 hover:bg-green-500 disabled:opacity-50 rounded-lg font-bold transition-all flex justify-center items-center gap-2"
                            >
                                {loading ? (
                                    <>
                                        <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                                        Deploying...
                                    </>
                                ) : "Launch Agent"}
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
