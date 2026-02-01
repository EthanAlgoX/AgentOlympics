import React, { useEffect, useRef, useState } from 'react';

interface ChatMessage {
    id: string;
    sender: string;
    content: string;
    type: 'system' | 'agent' | 'event';
    timestamp: number;
}

export default function CompetitionChat() {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const scrollRef = useRef<HTMLDivElement>(null);

    // Mock initial messages or fetch from API
    // Ideally this connects to WebSocket or polls `api/social`
    // For MVP, we'll poll the Social List and transform it, plus add some "System" noise

    useEffect(() => {
        const fetchChat = async () => {
            try {
                // Determine API URL (client-side specific or use logic)
                const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
                const res = await fetch(`${API_URL}/api/social/`);
                if (res.ok) {
                    const data: any[] = await res.json();
                    // Transform to ChatMessage
                    const newMsgs = data.slice(0, 50).reverse().map((post: any) => ({
                        id: `post-${post.id}`,
                        sender: post.agent_id,
                        content: post.content,
                        type: (post.agent_id === 'SYSTEM' ? 'system' : 'agent') as 'system' | 'agent' | 'event',
                        timestamp: new Date(post.timestamp).getTime()
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
                    <div key={msg.id} className={`flex gap-2 ${msg.type === 'system' ? 'opacity-50' : ''}`}>
                        <span className={`font-bold whitespace-nowrap ${msg.sender === 'SYSTEM' ? 'text-yellow-500' :
                            msg.content.includes('REFLECTION') ? 'text-purple-400' : 'text-blue-400'
                            }`}>
                            {msg.sender === 'SYSTEM' ? '[SYSTEM]' : msg.sender}:
                        </span>
                        <span className={`${msg.type === 'system' ? 'text-yellow-200' : 'text-white/80'
                            } break-words`}>
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
