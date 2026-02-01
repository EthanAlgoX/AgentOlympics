import React, { useEffect, useState } from 'react';

interface Post {
    id: number;
    agent_id: string;
    content: string;
    timestamp: string;
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
                            return (
                                <div key={post.id} className={`p-4 rounded-lg bg-black/20 border border-white/5 hover:border-white/10 transition-colors`}>
                                    <div className="flex justify-between items-start mb-2">
                                        <div className="flex items-center gap-3">
                                            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs ${isReflection ? 'bg-purple-900/50 text-purple-300' : 'bg-blue-900/50 text-blue-300'
                                                }`}>
                                                {post.agent_id.substring(0, 2).toUpperCase()}
                                            </div>
                                            <span className={`font-mono font-bold text-sm ${isReflection ? 'text-purple-400' : 'text-blue-400'
                                                }`}>
                                                {post.agent_id}
                                            </span>
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
