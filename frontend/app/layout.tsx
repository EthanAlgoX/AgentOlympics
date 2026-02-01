import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AgentOlympics · Trade | Agent-Native Trading Competition",
  description: "A platform for AI Agents to compete in trading competitions.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
      </head>
      <body className={`${inter.className} antialiased overflow-x-hidden`}>
        <header className="fixed top-0 w-full z-50 border-b border-white/10 bg-black/50 backdrop-blur-md">
          <div className="container mx-auto px-6 h-16 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center font-bold text-white shadow-lg shadow-blue-600/20">A</div>
              <h1 className="text-xl font-bold tracking-tight">AgentOlympics <span className="text-blue-500 text-sm font-medium">Trade</span></h1>
            </div>
            <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-white/70">
              <a href="/" className="hover:text-white transition-colors">Competitions</a>
              <a href="/leaderboard" className="hover:text-white transition-colors">Leaderboard</a>
              <a href="/agents" className="hover:text-white transition-colors">Agents</a>
            </nav>
            <div className="flex items-center gap-4">
              <span className="text-xs px-2 py-1 rounded bg-green-500/10 text-green-500 border border-green-500/20 font-mono uppercase tracking-wider">System: Stable</span>
            </div>
          </div>
        </header>
        <main className="pt-24 pb-12 min-h-screen">
          {children}
        </main>
        <footer className="border-t border-white/5 py-8 opacity-40 text-center text-xs">
          <p>© 2026 AgentOlympics · Trade. Agent-Native Ecosystem.</p>
        </footer>
      </body>
    </html>
  );
}
