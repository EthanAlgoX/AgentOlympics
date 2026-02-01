"use client";

export default function PnLChart({ data }: { data: number[] }) {
    if (!data || data.length === 0) return <div className="text-white/10 italic text-[10px]">Insufficient ledger data for PnL curve.</div>;

    const width = 400;
    const height = 150;
    const padding = 10;

    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min || 1;

    const points = data.map((val, i) => {
        const x = padding + (i / (data.length - 1 || 1)) * (width - 2 * padding);
        const y = height - padding - ((val - min) / range) * (height - 2 * padding);
        return `${x},${y}`;
    }).join(" ");

    return (
        <div className="w-full">
            <div className="flex justify-between items-center mb-2">
                <h4 className="text-[10px] font-bold text-white/30 uppercase tracking-widest">Performance Curve (Live)</h4>
                <span className={`text-[10px] font-mono ${data[data.length - 1] >= data[0] ? 'text-green-400' : 'text-red-400'}`}>
                    {((data[data.length - 1] - data[0]) / (data[0] || 1) * 100).toFixed(2)}%
                </span>
            </div>
            <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto overflow-visible">
                <defs>
                    <linearGradient id="pnlGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.4" />
                        <stop offset="100%" stopColor="#3b82f6" stopOpacity="0" />
                    </linearGradient>
                </defs>

                {/* Shadow/Fill area */}
                <polyline
                    fill="url(#pnlGradient)"
                    points={`${points} ${width - padding},${height - padding} ${padding},${height - padding}`}
                />

                {/* Main Line */}
                <polyline
                    fill="none"
                    stroke="#3b82f6"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    points={points}
                    className="drop-shadow-[0_0_8px_rgba(59,130,246,0.5)]"
                />

                {/* Current Point Marker */}
                {data.length > 0 && (
                    <circle
                        cx={padding + (data.length - 1) / (data.length - 1 || 1) * (width - 2 * padding)}
                        cy={height - padding - ((data[data.length - 1] - min) / range) * (height - 2 * padding)}
                        r="3"
                        fill="#3b82f6"
                    />
                )}
            </svg>
        </div>
    );
}
