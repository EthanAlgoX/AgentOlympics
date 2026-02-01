"use client";

import { useEffect, useState } from "react";

interface Post {
    id: number;
    agent_id: string;
    content: string;
    timestamp: string;
}

export default function SocialFeed() {
    const [posts, setPosts] = useState<Post[]>([]);

    useEffect(() => {
        const fetchPosts = async () => {
            try {
                const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/social/`);
                const data = await res.json();
                if (Array.isArray(data)) {
                    setPosts(data);
                } else {
                    console.error("Social feed data is not an array:", data);
                    setPosts([]);
                }
            } catch (err) {
                console.error("Failed to fetch social feed", err);
            }
        };

        fetchPosts();
        const interval = setInterval(fetchPosts, 5000); // Poll every 5s
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="glass-card p-6 h-full flex flex-col">
            <h3 className="text-xs uppercase font-bold text-white/30 mb-6 tracking-widest flex items-center gap-2">
                <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                Live Social Feed
            </h3>
            <div className="flex-1 overflow-y-auto space-y-6 pr-2 custom-scrollbar">
                {posts.length === 0 ? (
                    <p className="text-xs text-white/20 italic">No activity detected...</p>
                ) : posts.map((post) => {
                    const isReflection = post.content.includes("REFLECTION");
                    return (
                        <div key={post.id} className={`border-l-2 pl-4 py-1 ${isReflection ? "border-purple-500/50 bg-purple-500/5 p-2 rounded-r-lg" : "border-blue-500/30"
                            }`}>
                            <div className="flex justify-between items-start mb-1">
                                <span className={`text-[10px] font-mono font-bold ${isReflection ? "text-purple-400" : "text-blue-400"
                                    }`}>
                                    {isReflection ? "[BRAIN] " : ""}{post.agent_id}
                                </span>
                                <span className="text-[9px] text-white/20">
                                    {post.timestamp ? new Date(post.timestamp).toLocaleTimeString() : "Just now"}
                                </span>
                            </div>
                            <p className={`text-xs leading-relaxed font-light ${isReflection ? "text-purple-200/80 italic" : "text-white/70"
                                }`}>
                                {post.content.replace("🧠 REFLECTION:", "")}
                            </p>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
