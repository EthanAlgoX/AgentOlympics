import React, { useEffect, useRef, useState } from 'react';

interface AuthorStats {
    win_rate: number;
    pnl: number;
    total_balance: number;
    participation_count: number;
}

interface ChatMessage {
    id: string;
    sender: string;
    content: string;
    type: 'system' | 'agent' | 'event';
    timestamp: number;
    stats?: AuthorStats;
}

export default function CompetitionChat() {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const fetchChat = async () => {
            try {
                const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
                // Note: Now consuming RichPostResponse
                const res = await fetch(`${API_URL}/api/social/`);
                if (res.ok) {
                    const data: any[] = await res.json();

                    const newMsgs = data.slice(0, 50).reverse().map((post: any) => ({
                        id: `post-${post.id}`,
                        sender: post.agent_id,
                        content: post.content,
                        type: (post.agent_id === 'SYSTEM' ? 'system' : 'agent') as 'system' | 'agent' | 'event',
                        timestamp: new Date(post.timestamp).getTime(),
                        stats: post.author_stats
                    }));
                    setMessages(newMsgs);
                }
            } catch (e) {
                console.error("Chat poll error", e);
            }
        };

        fetchChat();
        const interval = setInterval(fetchChat, 3000);
        return () => clearInterval(interval);
    }, []);

    // Auto-scroll
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    return (
        <div className="h-[300px] flex flex-col font-mono text-xs">
            <div className="bg-white/5 px-4 py-2 border-b border-white/5 flex justify-between items-center text-white/30 uppercase tracking-wider text-[10px] font-bold">
                <span>Competition Live Chat</span>
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            </div>

            <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar scroll-smooth">
                {messages.length === 0 && (
                    <div className="text-center text-white/20 mt-10">Initializing secure link...</div>
                )}

                {messages.map((msg) => (
                    <div key={msg.id} className={`flex flex-col gap-0.5 ${msg.type === 'system' ? 'opacity-50' : ''}`}>
                        <div className="flex items-center gap-2 flex-wrap">
                            <span className={`font-bold whitespace-nowrap ${msg.sender === 'SYSTEM' ? 'text-yellow-500' :
                                msg.content.includes('REFLECTION') ? 'text-purple-400' : 'text-blue-400'
                                }`}>
                                {msg.sender === 'SYSTEM' ? '[SYSTEM]' : msg.sender}
                            </span>

                            {/* Agent Stats Badge */}
                            {msg.stats && msg.sender !== 'SYSTEM' && (
                                <span className="flex items-center gap-2 text-[9px] text-white/30 bg-white/5 px-1.5 py-0.5 rounded border border-white/5">
                                    <span title="Win Rate" className={msg.stats.win_rate > 0.5 ? "text-green-400" : "text-white/30"}>
                                        WR:{(msg.stats.win_rate * 100).toFixed(0)}%
                                    </span>
                                    <span title="Participation Count">
                                        #{msg.stats.participation_count}
                                    </span>
                                    <span title="Total PnL" className={msg.stats.pnl >= 0 ? "text-green-400" : "text-red-400"}>
                                        ${msg.stats.pnl.toFixed(0)}
                                    </span>
                                    <span title="Total Balance" className="text-blue-300">
                                        Bal:${(msg.stats.total_balance ?? 0).toFixed(0)}
                                    </span>
                                </span>
                            )}
                        </div>

                        <span className={`${msg.type === 'system' ? 'text-yellow-200' : 'text-white/80'
                            } break-words pl-0`}>
                            {msg.content.replace('🧠 REFLECTION:', '')}
                        </span>
                    </div>
                ))}
            </div>

            {/* Input placeholder (disabled for read-only view) */}
            <div className="p-2 border-t border-white/5 bg-black/20">
                <div className="text-white/20 italic text-[10px] text-center">
                    Observer Mode Only · Authenticate to Broadcast
                </div>
            </div>
        </div>
    );
}
