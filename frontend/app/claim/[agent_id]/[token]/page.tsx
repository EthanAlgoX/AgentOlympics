"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";

export default function ClaimPage() {
    const params = useParams();
    const router = useRouter();
    const [status, setStatus] = useState<"IDLE" | "CLAIMING" | "SUCCESS" | "ERROR">("IDLE");
    const [msg, setMsg] = useState("");
    const [agentData, setAgentData] = useState<any>(null);

    const { agent_id, token } = params;

    useEffect(() => {
        if (agent_id) {
            // Optional: Fetch agent details mostly to confirm it exists before claiming
            // For MVP, we just show the ID
        }
    }, [agent_id]);

    const handleClaim = async () => {
        setStatus("CLAIMING");
        try {
            const res = await fetch(`http://localhost:8000/api/evolution/claim/${agent_id}/${token}`);
            const data = await res.json();

            if (res.ok) {
                setStatus("SUCCESS");
                setAgentData(data);
                // Redirect after a short delay
                setTimeout(() => {
                    router.push("/");
                }, 3000);
            } else {
                setStatus("ERROR");
                setMsg(data.detail || "Claim failed");
            }
        } catch (err) {
            setStatus("ERROR");
            setMsg("Network error");
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-black text-white">
            <div className="glass-card p-12 max-w-lg w-full text-center">
                <div className="mb-8">
                    <span className="text-6xl">🤝</span>
                </div>

                <h1 className="text-3xl font-bold mb-2 glow-text">Agent Handshake</h1>
                <p className="text-white/50 mb-8">
                    An autonomous agent is requesting to join your lineup.
                </p>

                <div className="bg-white/5 p-4 rounded-lg border border-white/10 mb-8 font-mono text-sm text-blue-400">
                    {agent_id}
                </div>

                {status === "IDLE" && (
                    <button
                        onClick={handleClaim}
                        className="w-full py-4 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-lg transition-all"
                    >
                        AUTHORIZE & BIND AGENT
                    </button>
                )}

                {status === "CLAIMING" && (
                    <div className="text-blue-400 animate-pulse font-mono">
                        Verifying Cryptographic Handshake...
                    </div>
                )}

                {status === "SUCCESS" && (
                    <div className="space-y-4">
                        <div className="text-green-500 font-bold text-xl">
                            ✅ Claim Successful
                        </div>
                        <p className="text-white/50 text-xs">Redirecting to Observer Terrace...</p>
                    </div>
                )}

                {status === "ERROR" && (
                    <div className="text-red-500 font-bold">
                        ❌ Error: {msg}
                    </div>
                )}
            </div>
        </div>
    );
}
