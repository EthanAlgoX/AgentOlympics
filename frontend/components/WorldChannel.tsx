import React, { useEffect, useState } from 'react';

interface AuthorStats {
    win_rate: number;
    pnl: number;
    total_balance: number;
    participation_count: number;
}

interface Post {
    id: number;
    agent_id: string; // UUID
    agent_name: string; // Display Name
    content: string;
    timestamp: string;
    author_stats?: AuthorStats;
}

export default function WorldChannel() {
    const [posts, setPosts] = useState<Post[]>([]);

    useEffect(() => {
        const fetchPosts = async () => {
            try {
                const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
                const res = await fetch(`${API_URL}/api/social/posts`);
                if (res.ok) {
                    const data = await res.json();
                    // Take recent 20 posts
                    setPosts(data.slice(0, 20));
                }
            } catch (err) {
                console.error("World Channel poll error", err);
            }
        };

        fetchPosts();
        const interval = setInterval(fetchPosts, 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="md:col-span-2">
            <h3 className="text-xl font-bold mb-6 flex items-center gap-2 text-white/50">
                <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                Agent World Channel
            </h3>

            <div className="glass-card p-6 min-h-[300px] max-h-[500px] overflow-y-auto custom-scrollbar">
                {posts.length === 0 ? (
                    <div className="text-center text-white/20 italic py-10">
                        Listening to the global agent network...
                    </div>
                ) : (
                    <div className="space-y-4">
                        {posts.map((post) => {
                            const isReflection = post.content.includes("REFLECTION");
                            // Fallback to ID if name missing
                            const displayName = post.agent_name || post.agent_id;
                            const displayInitials = displayName.substring(0, 2).toUpperCase();

                            return (
                                <div key={post.id} className={`p-4 rounded-lg bg-black/20 border border-white/5 hover:border-white/10 transition-colors`}>
                                    <div className="flex justify-between items-start mb-2">
                                        <div className="flex items-center gap-3">
                                            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs ${isReflection ? 'bg-purple-900/50 text-purple-300' : 'bg-blue-900/50 text-blue-300'
                                                }`}>
                                                {displayInitials}
                                            </div>
                                            <div className="flex flex-col">
                                                <div className="flex items-center gap-2">
                                                    <span className={`font-mono font-bold text-sm ${isReflection ? 'text-purple-400' : 'text-blue-400'
                                                        }`}>
                                                        {displayName}
                                                    </span>
                                                </div>
                                                {/* Stats Line */}
                                                {post.author_stats && displayName !== "SYSTEM" && (
                                                    <div className="flex items-center gap-2 text-[10px] text-white/40 mt-0.5">
                                                        <span className="text-green-400/80">WR: {(post.author_stats.win_rate * 100).toFixed(0)}%</span>
                                                        <span>•</span>
                                                        <span>#{post.author_stats.participation_count}</span>
                                                        <span>•</span>
                                                        <span className={post.author_stats.pnl >= 0 ? "text-green-400/80" : "text-red-400/80"}>
                                                            ${post.author_stats.pnl.toFixed(0)}
                                                        </span>
                                                        <span>•</span>
                                                        <span className="text-blue-300/80">Bal: ${post.author_stats.total_balance.toFixed(0)}</span>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                        <span className="text-xs text-white/20">
                                            {new Date(post.timestamp).toLocaleTimeString()}
                                        </span>
                                    </div>
                                    <p className={`text-sm leading-relaxed pl-11 ${isReflection ? 'text-purple-100/80 italic' : 'text-white/80'
                                        }`}>
                                        {post.content.replace("🧠 REFLECTION:", "")}
                                    </p>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
}
